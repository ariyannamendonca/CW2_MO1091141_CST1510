import streamlit as st

st.set_page_config(page_title="Login/Register", page_icon="🔑", layout="centered")

#initalise session state
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

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
        if login_username in users and users[login_username] == login_password:
            st.session_state.logged_in = True
            st.session_state.username = login_username
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
    st.session_state.users[new_username] = new_password
    st.success("Account created! You can now log in from the login tab.")
    st.info("Tip: go to the Login tab and sign in with your new account.")