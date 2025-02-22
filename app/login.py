import streamlit as st
import requests
from api_utils import login_user, logout_user, is_valid_email, is_valid_password
from reset_password import show_reset_password  # Import the reset password module

def show_login_page():
    st.title("Welcome to Airline Assistant")

    # Initialize session states if not already set
    if 'signup_success' not in st.session_state:
        st.session_state.signup_success = False
    if 'success_message' not in st.session_state:
        st.session_state.success_message = ""
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Login"
    if 'show_reset_password' not in st.session_state:
        st.session_state.show_reset_password = False

    # Conditional rendering: if "Forgot Password?" is clicked, show Reset Password
    if st.session_state.show_reset_password:
        show_reset_password()
        return

    # Create tabs for Login and Sign-Up
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # Login Tab
    with tab1:
        st.subheader("Login to Your Account")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if login_username and login_password:
                if login_user(login_username, login_password):
                    st.session_state.success_message = "Logged in successfully!"
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")

        # Display login success message if present
        if st.session_state.success_message:
            st.success(st.session_state.success_message)
            st.session_state.success_message = ""

        # Add "Forgot Password?" button
        if st.button("Forgot Password?"):
            st.session_state.show_reset_password = True
            st.rerun()

    # Sign-Up Tab
    with tab2:
        st.subheader("Create a New Account")
        signup_username = st.text_input("Username", key="signup_username")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up"):
            if signup_password != confirm_password:
                st.error("Passwords do not match")
            elif not signup_username or not signup_password:
                st.error("Please fill in all fields")
            elif not is_valid_email(signup_username):
                st.error("Invalid email format")
            elif not is_valid_password(signup_password):
                st.error("Invalid password format. Must be at least 8 characters, with 1 numeral and 1 special character.")
            else:
                try:
                    response = requests.post(
                        "http://localhost:8000/create-user",
                        json={
                            "username": signup_username,
                            "password": signup_password
                        }
                    )
                    
                    if response.status_code == 200:
                        st.session_state.signup_success = True
                    else:
                        error_msg = response.json().get('detail', 'Registration failed')
                        st.error(f"Registration failed: {error_msg}")
                        
                except Exception as e:
                    st.error(f"Registration error: {str(e)}")

        # Display signup success message if flag is set
        if st.session_state.signup_success:
            st.success("Account created successfully! Please login.")
            st.session_state.signup_success = False  # Reset the flag after showing message

def show_logout_button():
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()
