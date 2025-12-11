import os
import bcrypt
import streamlit as st

USER_FILE = "DATA/user.txt"

def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    username, hashed_pw, role = parts
                    users[username] = {"password" : hashed_pw, "role" : role}
    return users

def save_user(username, hashed_pw, role="user"):
    with open(USER_FILE, "a") as f:
        f.write(f"{username},{hashed_pw},{role}\n")

st.set_page_config(page_title="Login/Register", page_icon="🔑", layout="centered")

#initalise session state
if "users" not in st.session_state:
    st.session_state.users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
st.title("🔐 Welcome")

#if already logged in go straight to dashboard
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

#tabs: login/register
tab_login, tab_register = st.tabs(["Login", "Register"])

#login tab
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", key="login_password")

    if st.button("Log in", type="primary"):
        users= st.session_state.users
        
        if login_username in users:
            stored_hash = users[login_username]["password"]
            role = users[login_username]["role"]
            
            if bcrypt.checkpw(login_password.encode(), stored_hash.encode()):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.session_state.role = role
                st.success(f"Welcome back, {login_username}!🎉 ")

            #redirect to dashboard page
            st.switch_page("pages./1_Dashboard.py")
        else:
            st.error("Invalid username or password.")

#register tab
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

#basic checks
if not new_username or not new_password:
    st.warning("Please fill in all fields.")
elif new_password != confirm_password:
    st.warning("Passwords don't match.")
elif new_username in st.session_state.users:
    st.error("Username already exists. Choose another username.")
else:

    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    save_user(new_username, hashed_pw,"user")
    st.session_state.users[new_username] = {"password" : hashed_pw, "role" : "user"}

    st.success("Account created! You can now log in from the login tab.")
    st.info("Tip: go to the Login tab and sign in with your new account.")