import streamlit as st
import hashlib
import requests

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_login_form():
    with st.sidebar:
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            hashed_pw = hash_password(password)
            if verify_user(username, hashed_pw):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")

def verify_user(username, password_hash):
    try:
        response = requests.post(
            "http://localhost:8000/verify-user",
            json={"username": username, "password_hash": password_hash}
        )
        return response.json().get("valid", False)
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False
    
def show_signup_form():
    with st.sidebar:
        st.header("Sign Up")
        new_username = st.text_input("Choose a username", key="signup_username")
        new_password = st.text_input("Choose a password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm_password")
        
        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            elif not new_username or not new_password:
                st.error("Username and password are required!")
            else:
                hashed_pw = hash_password(new_password)
                try:
                    response = requests.post(
                        "http://localhost:8000/create-user",
                        json={"username": new_username, "password_hash": hashed_pw}
                    )
                    if response.status_code == 200:
                        st.success("Account created successfully! Please log in.")
                    else:
                        st.error(f"Failed to create account: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

def verify_password(username, password):
    password_hash = hash_password(password)
    return verify_user(username, password_hash)


def create_user(username: str, password_hash: str) -> bool:
    """Simple user creation function"""
    try:
        response = requests.post(
            "http://localhost:8000/create-user",
            json={"username": username, "password_hash": password_hash}
        )
        return response.status_code == 200
    except Exception:
        return False

