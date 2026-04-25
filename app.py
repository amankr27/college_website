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
cursor.execute("SELECT 1 FROM users WHERE username=?", ("admin",))
if not cursor.fetchone():
    add_user("admin", "admin123", "admin")

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
    st.title("👨‍💼 Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["👥 Users", "📩 Messages", "📊 Overview"])

    # ---------------- USERS MANAGEMENT ----------------
    with tab1:
        st.subheader("Manage Users")

        users = cursor.execute(
            "SELECT id, username, role FROM users"
        ).fetchall()

        if users:
            for user in users:
                col1, col2, col3, col4 = st.columns([2,2,2,2])

                with col1:
                    st.write(user[0])  # ID
                with col2:
                    st.write(user[1])  # Username
                with col3:
                    st.write(user[2])  # Role

                # Delete User
                with col4:
                    if st.button("❌ Delete", key=f"del_{user[0]}"):
                        cursor.execute("DELETE FROM users WHERE id=?", (user[0],))
                        conn.commit()
                        st.success(f"User {user[1]} deleted")
                        st.rerun()

            st.divider()

            # Change Role
            st.subheader("Change User Role")
            usernames = [u[1] for u in users]

            selected_user = st.selectbox("Select User", usernames)
            new_role = st.selectbox("Select Role", ["user", "admin"])

            if st.button("Update Role"):
                cursor.execute(
                    "UPDATE users SET role=? WHERE username=?",
                    (new_role, selected_user)
                )
                conn.commit()
                st.success("Role updated")
                st.rerun()
        else:
            st.info("No users found")

    # ---------------- MESSAGES MANAGEMENT ----------------
    with tab2:
        st.subheader("Manage Messages")

        contacts = cursor.execute(
            "SELECT id, name, email, message FROM contacts"
        ).fetchall()

        if contacts:
            for msg in contacts:
                st.write(f"**{msg[1]}** ({msg[2]})")
                st.write(msg[3])

                if st.button("🗑 Delete Message", key=f"msg_{msg[0]}"):
                    cursor.execute("DELETE FROM contacts WHERE id=?", (msg[0],))
                    conn.commit()
                    st.success("Message deleted")
                    st.rerun()

                st.divider()
        else:
            st.info("No messages found")

    # ---------------- OVERVIEW / ANALYTICS ----------------
    with tab3:
        st.subheader("Website Overview")

        total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_msgs = cursor.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Users", total_users)

        with col2:
            st.metric("Total Messages", total_msgs)

        st.success("System running normally ✅")
# -------------------- LOGIN PAGE --------------------

def login_page():
    st.subheader("Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # LOGIN
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.role = user[1]
                st.success(f"Welcome {user[0]}")
                st.rerun()
            else:
                st.error("Invalid credentials")

        if st.session_state.logged_in:
            st.write(f"Logged in as {st.session_state.username}")
            if st.button("Logout"):
                logout()
                st.rerun()

    # REGISTER
    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register"):
            if new_pass == confirm:
                if not is_username_taken(new_user):
                    add_user(new_user, new_pass)
                else:
                    st.error("Username already exists")
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
    st.title("🎓 College Website")

    # Menu
    menu = ["Home", "Login", "Contact"]

    # Show Admin only if logged in as admin
    if st.session_state.get("logged_in") and st.session_state.get("role") == "admin":
        menu.append("Admin")

    choice = st.sidebar.selectbox("Menu", menu)

    # ---------------- HOME ----------------
    if choice == "Home":
        st.subheader("Welcome to College Website")
        st.image("image1.jpg", caption="Our College", use_column_width=True)


    # ---------------- LOGIN ----------------
    elif choice == "Login":
        login_page()

    # ---------------- CONTACT ----------------
    elif choice == "Contact":
        contact_page()

    # ---------------- ADMIN ----------------
    elif choice == "Admin":
        if st.session_state.get("logged_in") and st.session_state.get("role") == "admin":
            admin_panel()
        else:
            st.error("🔒 Access denied. Admins only.")
    

# -------------------- RUN --------------------

if __name__ == "__main__":
    main()
