import streamlit as st
import requests
from api_utils import login_user, logout_user


def show_login_page():
    st.title("Welcome to Airline Assistant")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login_username and login_password:
                if login_user(login_username, login_password):
                    st.success("Logged in successfully!")
                    st.rerun()
            else:
                st.error("Please enter both username and password")
    
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
            else:
                try:
                    # Call the backend /create-user endpoint directly
                    response = requests.post(
                        "http://localhost:8000/create-user",
                        json={
                            "username": signup_username,
                            "password": signup_password
                        }
                    )
                    
                    if response.status_code == 200:
                        st.success("Account created successfully! Please login.")
                        # Switch to login tab
                        st.session_state.active_tab = "Login"
                        st.rerun()
                    else:
                        error_msg = response.json().get('detail', 'Registration failed')
                        st.error(f"Registration failed: {error_msg}")
                        
                except Exception as e:
                    st.error(f"Registration error: {str(e)}")

def show_logout_button():
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()
