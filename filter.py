import imaplib
import email
import re
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, simpledialog
from threading import Thread

# Global variables to store IMAP connection and credentials
mail = None
username = None
password = None

# Function to connect to the IMAP server
def connect_to_server(email_address, email_password, server="imap.gmail.com"):
    global mail
    mail = imaplib.IMAP4_SSL(server)
    try:
        mail.login(email_address, email_password)
        messagebox.showinfo("Login", "Login successful.")
        return True
    except imaplib.IMAP4.error as e:
        messagebox.showerror("Error", f"Login failed: {e}")
        return False

# Function to handle login button click event
def login():
    global username, password
    username = email_entry.get()
    password = password_entry.get()
    if username and password:
        if connect_to_server(username, password):
            save_credentials()
            login_window.destroy()
            show_welcome_page()
    else:
        messagebox.showerror("Error", "Please enter both username and password.")

# Function to initialize the login GUI
def initialize_login_gui():
    global login_window, email_entry, password_entry

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x150")

    login_frame = tk.Frame(login_window)
    login_frame.pack(pady=20)

    email_label = tk.Label(login_frame, text="Email:", font=("Helvetica", 12))
    email_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
    email_entry = tk.Entry(login_frame, font=("Helvetica", 12), width=20)
    email_entry.grid(row=0, column=1, padx=10, pady=5)

    password_label = tk.Label(login_frame, text="Password:", font=("Helvetica", 12))
    password_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    password_entry = tk.Entry(login_frame, show="*", font=("Helvetica", 12), width=20)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    load_saved_credentials()

    login_button = tk.Button(login_frame, text="Login", command=login, font=("Helvetica", 12))
    login_button.grid(row=2, columnspan=2, pady=10)

    # Center the login window on the screen
    center_window(login_window)

    login_window.mainloop()

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x_offset = (window.winfo_screenwidth() - width) // 2
    y_offset = (window.winfo_screenheight() - height) // 2
    window.geometry(f"+{x_offset}+{y_offset}")


# Function to save login credentials
def save_credentials():
    global username
    username = email_entry.get()
    if username:
        with open("credentials.txt", "w") as file:
            file.write(username)

def load_saved_credentials():
    try:
        with open("credentials.txt", "r") as file:
            saved_username = file.readline().strip()
            if saved_username:
                email_entry.insert(0, saved_username)
    except FileNotFoundError:
        pass

# Function to display welcome page with options
def show_welcome_page():
    global welcome_window

    welcome_window = tk.Toplevel()
    welcome_window.title("Welcome")
    welcome_window.geometry("400x300")

    # Create and pack the welcome label
    welcome_label = tk.Label(welcome_window, text="Welcome to Email Filter", fg="white", font=("Helvetica", 24, "bold"))
    welcome_label.pack(pady=50)  # Increase padding to move the label towards the center

    # Center the welcome window on the screen
    center_window(welcome_window)

    # Create the three dots button and attach the show_options function to it
    three_dots_button = tk.Button(welcome_window, text="⋮", command=show_options)
    three_dots_button.place(x=10, y=10)  # Position the button at the top left corner

    welcome_window.mainloop()


# Function to show additional options
def show_options():
    global welcome_window

    options_menu = tk.Menu(welcome_window, tearoff=0)
    options_menu.add_command(label="Change Mail Account", command=change_mail_account)
    options_menu.add_command(label="Run Filter", command=run_filter)
    options_menu.add_command(label="View Spam", command=view_spam)
    options_menu.add_command(label="View Inbox", command=view_inbox)

    try:
        options_menu.tk_popup(welcome_window.winfo_pointerx(), welcome_window.winfo_pointery())
    finally:
        options_menu.grab_release()

# Function to change mail account
def change_mail_account():
    global welcome_window
    welcome_window.destroy()
    initialize_login_gui()

# Function to handle filter button click event
def run_filter():
    def run_filter_task():
        # Your filter task code goes here
        pass

    def show_filter_result():
        # Your filter result display code goes here
        pass

    # Simulating filter progress window
    progress_window = tk.Toplevel()
    progress_window.title("Filter Progress")
    progress_window.geometry("300x100")

    progress_label = tk.Label(progress_window, text="Filter is running...")
    progress_label.pack(pady=10)

    progress_window.after(5000, show_filter_result)  # Simulating after 5 seconds
    progress_window.after(6000, progress_window.destroy)  # Simulating after 6 seconds

# Function to handle spam button click event
def view_spam():
    spam_emails = retrieve_emails("[Gmail]/Spam")
    show_emails_window("Spam", spam_emails)

# Function to handle inbox button click event
def view_inbox():
    inbox_emails = retrieve_emails("INBOX")
    show_emails_window("Inbox", inbox_emails)

# Function to retrieve emails from a specified folder
def retrieve_emails(folder):
    global mail
    select_folder(folder)
    result, data = mail.search(None, 'ALL')
    if result == "OK":
        return data[0].split() if data else []
    else:
        messagebox.showerror("Error", f"Error searching {folder}: {result}")
        return []

# Function to select a mailbox folder
def select_folder(folder):
    global mail
    mail.select(folder)

# Function to move emails to a specified folder
def move_emails(msg_ids, destination_folder):
    global mail
    for msg_id in msg_ids:
        mail.copy(msg_id, destination_folder)
        mail.store(msg_id, '+FLAGS', '\\Deleted')
    mail.expunge()

# Function to read spam words from a text file
def read_spam_words(filename):
    with open(filename, 'r') as file:
        spam_words = file.read().splitlines()
    return spam_words

# Function to retrieve and process new emails
def retrieve_and_process_new_emails(spam_words, additional_phishing_domains=None):
    global mail
    select_folder("INBOX")
    result, data = mail.search(None, 'ALL')
    if result == "OK":
        msg_ids = data[0].split() if data else []
        if msg_ids:
            phishing_domains = read_phishing_domains("phishing_domains.txt")
            if additional_phishing_domains:
                phishing_domains += additional_phishing_domains
            for msg_id in msg_ids:
                result, data = mail.fetch(msg_id, "(RFC822)")
                if result == "OK":
                    raw_email = data[0][1]
                    if raw_email is None:
                        print(f"Failed to fetch email data for message ID: {msg_id}")
                        continue
                    msg = email.message_from_bytes(raw_email)
                    if not msg['Subject']:
                        move_emails([msg_id], "[Gmail]/Spam")
                        print("Email with no subject moved to spam folder.")
                        continue
                    email_body = ""
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            email_body += part.get_payload(decode=True).decode()
                    if len(email_body.split()) < 2:
                        move_emails([msg_id], "[Gmail]/Spam")
                        print(f"Email with subject '{msg['Subject']}' moved to spam folder because it has less than 2 words in the body.")
                        continue
                    if contains_links(email_body):
                        move_emails([msg_id], "[Gmail]/Spam")
                        print(f"Email with subject '{msg['Subject']}' moved to spam folder because it contains a link.")
                        continue
                    if contains_phishing_link(email_body, phishing_domains):
                        move_emails([msg_id], "[Gmail]/Spam")
                        print(f"Email with subject '{msg['Subject']}' moved to spam folder because it contains a phishing link.")
                        continue
                    spam_found = False
                    for word in spam_words:
                        if word.lower() in email_body.lower():
                            move_emails([msg_id], "[Gmail]/Spam")
                            print(f"Email with subject '{msg['Subject']}' moved to spam folder because it contains a spam word: {word}.")
                            spam_found = True
                            break
                    if not spam_found:
                        print(f"Email with subject '{msg['Subject']}' processed successfully.")
                else:
                    print(f"Failed to fetch email data for message ID: {msg_id}")
        else:
            print("No new emails found.")
    else:
        print("Error searching emails:", result)

# Function to show emails in a new window
def show_emails_window(folder, emails):
    email_window = tk.Toplevel()
    email_window.title(f"{folder} Emails")
    email_window.geometry("800x600")
    
    if emails:
        email_frame = tk.Frame(email_window)
        email_frame.pack(fill=tk.BOTH, expand=True)
        text_area = scrolledtext.ScrolledText(email_frame, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)
        for email_id in emails:
            result, data = mail.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)                                                                                                                                          
            email_body = ""
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    email_body += part.get_payload(decode=True).decode()
            text_area.insert(tk.END, f"From: {msg['From']}\nTo: {msg['To']}\nSubject: {msg['Subject']}\n\n{email_body}\n\n{'=' * 50}\n\n")
        text_area.config(state=tk.DISABLED)
    else:
        tk.Label(email_window, text=f"No emails in {folder}").pack(pady=20)

# Function to check for links in the email body
def contains_links(email_body):
    url_pattern = r'(https?://\S+)'
    urls = re.findall(url_pattern, email_body)
    return len(urls) > 0

# Function to read phishing domains from a text file
def read_phishing_domains(filename):
    with open(filename, 'r') as file:
        phishing_domains = file.read().splitlines()
    return phishing_domains

# Function to check if an email contains a phishing link
def contains_phishing_link(email_body, phishing_domains):
    url_pattern = r'(https?://\S+)'
    urls = re.findall(url_pattern, email_body)
    for url in urls:
        for domain in phishing_domains:
            if domain.lower() in url.lower():
                return True
    return False

if __name__ == "__main__":
    initialize_login_gui()