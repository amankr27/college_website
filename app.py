import streamlit as st
import sqlite3
import re
import hashlib

# -------------------- DATABASE --------------------

conn = sqlite3.connect("college.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT,
role TEXT DEFAULT 'user'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS contacts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
message TEXT
)
''')

conn.commit()

# -------------------- SESSION --------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = "user"

# -------------------- SECURITY --------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------- FUNCTIONS --------------------

def is_username_taken(username):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone() is not None

def add_user(username, password, role="user"):
    try:
        cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role)
        )
        conn.commit()
        st.success("Registration successful!")
    except sqlite3.IntegrityError:
        st.error("Username already exists")

def login_user(username, password):
    cursor.execute(
    "SELECT username, role FROM users WHERE username=? AND password=?",
    (username, hash_password(password))
    )
    return cursor.fetchone()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "user"
    st.success("Logged out")

def insert_contact(name, email, message):
    cursor.execute(
    "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
    (name, email, message)
    )
    conn.commit()
    st.success("Message submitted")

def valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

# -------------------- ADMIN PANEL --------------------

def admin_panel():
    st.subheader("Admin Dashboard")
    
    st.write("### Users")
    users = cursor.execute("SELECT id, username, role FROM users").fetchall()
    st.table(users)
    
    st.write("### Contact Messages")
    contacts = cursor.execute("SELECT * FROM contacts").fetchall()
    st.table(contacts)

# -------------------- LOGIN PAGE --------------------

def login_page():
    st.subheader("Login")
    
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

if st.button("Login"):
    user = login_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.username = user[0]
        st.session_state.role = user[1]
        st.success(f"Welcome {user[0]}")
    else:
        st.error("Invalid credentials")

if st.session_state.logged_in:
    st.write(f"Logged in as {st.session_state.username}")
    if st.button("Logout"):
        logout()

# Register
st.subheader("Register")
new_user = st.text_input("New Username")
new_pass = st.text_input("New Password", type="password")
confirm = st.text_input("Confirm Password", type="password")

if st.button("Register"):
    if new_pass == confirm:
        if not is_username_taken(new_user):
            add_user(new_user, new_pass)
        else:
            st.error("Username exists")
    else:
        st.error("Passwords do not match")


# -------------------- CONTACT --------------------

def contact_page():
    st.subheader("Contact")
    
    
    name = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message")

    if st.button("Submit"):
        if valid_email(email):
            insert_contact(name, email, message)
        else:
            st.error("Invalid email")


# -------------------- MAIN UI --------------------

def main():
    st.title("College Website")
    
    menu = ["Home", "Login", "Contact"]
    if st.session_state.role == "admin":
        menu.append("Admin")
    
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Home":
        st.write("Welcome to College Website")
    
    elif choice == "Login":
        login_page()
    
    elif choice == "Contact":
        contact_page()
    
    elif choice == "Admin":
        if st.session_state.role == "admin":
            admin_panel()
        else:
            st.error("Access denied")
    

# -------------------- RUN --------------------

if __name__ == "__main__":
    main()
