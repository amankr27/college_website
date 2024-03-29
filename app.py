import streamlit as st
import mysql.connector
import re

# Connect to MySQL
db_connection = mysql.connector.connect(
    host="sql6.freesqldatabase.com",
    user="sql6690368",
    password="Ba7pS2rs9e",
    database="sql6690368"
)
cursor = db_connection.cursor()

# Create a users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username TEXT,
        password TEXT
    )
''')
db_connection.commit()

# Create a contacts table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        message TEXT
    )
''')
db_connection.commit()

# Session state to track user login status
class SessionState:
    def __init__(self):
        self.logged_in = False

session_state = SessionState()

# Streamlit app

# Function to check if the new username is already taken
def is_username_taken(new_username):
    cursor.execute("SELECT * FROM users WHERE username = %s", (new_username,))
    result = cursor.fetchone()
    return result is not None

def main():
    st.title("College Website")

    # Navigation
    menu = ["Home", "Login", "Contact"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        st.write("""
        Welcome to our College Website!

        Here, you can find information about our courses, faculty, and events.
        Explore the website to discover more about our academic programs and campus life.
        """)

        st.image("image1.jpg", caption="Our College", use_column_width=True)

        st.write("""
        If you have any questions or need assistance, feel free to contact us through the 'Contact' page.
        """)

    elif choice == "Login":
        st.subheader("Login")
        login()

    elif choice == "Contact":
        st.subheader("Contact Us")
        contact()

# login() function
def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check login credentials against the database
        if is_valid_login(username, password):
            # Set a session variable or display a success message
            session_state.logged_in = True
            st.success("Logged in as {}".format(username))
        else:
            st.error("Invalid username or password")

        # Add a "Logout" button when logged in
        if session_state.logged_in:
            if st.button("Logout"):
                logout()

    # Registration form
    st.subheader("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if new_password == confirm_password:
            # Check if the new username is already taken
            if not is_username_taken(new_username):
                # Add user to the database
                add_user(new_username, new_password)
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username is already taken. Please choose a different one.")
        else:
            st.error("Passwords do not match. Please confirm your password.")

def is_valid_login(username, password):
    # Query the database to check if the provided credentials are valid
    try:
        cursor.execute('''
            SELECT * FROM users WHERE username = %s AND password = %s
        ''', (username, password))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        st.error(f"Error checking login credentials: {str(e)}")
        return False

# Function to add user to the database
def add_user(username, password):
    try:
        cursor.execute('''
            INSERT INTO users (username, password) VALUES (%s, %s)
        ''', (username, password))
        db_connection.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062:
            st.error("Error adding user to the database: Username is already taken.")
        else:
            st.error(f"Error adding user to the database: {str(err)}")

# Logout function
def logout():
    # Clear the session state to indicate the user is logged out
    session_state.logged_in = False
    st.success("Logged out successfully")

# Inside the contact() function
def contact():
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")

    if st.button("Submit"):
        # Add contact form submission logic and database connection here
        if is_valid_email(email):
            insert_contact_data(name, email, message)
            st.success("Message submitted successfully")
        else:
            st.error("Invalid email address. Please provide a valid email.")

def is_valid_email(email):
    # Email validation using a regular expression
    email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return bool(re.match(email_pattern, email))

def insert_contact_data(name, email, message):
    # Add contact form submission logic and database connection here
    try:
        cursor.execute('''
            INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)
        ''', (name, email, message))
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()
        st.error(f"Error submitting message: {str(e)}")



if __name__ == '__main__':
    main()
