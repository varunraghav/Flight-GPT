import requests
import streamlit as st
import re

def get_api_response(question, session_id, model):
    # Check if user is authenticated and has token
    if "token" not in st.session_state or not st.session_state.token:
        st.error("No authentication token found. Please login again.")
        return None

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {st.session_state.token}"  # Add JWT token
    }

    data = {
        "question": question,
        "model": model
    }

    if session_id:
        data["session_id"] = session_id
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state.authenticated = False
            st.session_state.token = None
            return None
        else:
            st.error(f"API Error: {response.status_code}\n{response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None
    
def get_direct_api_response(question, session_id, model):
    # Initialize message count if not already present
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    # Check if the user has reached the message limit
    if st.session_state.message_count >= 5:
        st.error("You have reached the maximum number of messages. Please login to continue.")
        return None

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    data = {
        "question": question,
        "model": model
    }

    if session_id:
        data["session_id"] = session_id

    try:
        response = requests.post(
            "http://localhost:8000/direct_chat",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            st.session_state.message_count += 1  # Increment message count
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}\n{response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None


def login_user(username: str, password: str) -> bool:
    """
    Authenticate user and get JWT token
    """
    try:
        response = requests.post(
            "http://localhost:8000/token",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            st.session_state.authenticated = True
            st.session_state.username = username
            return True
        else:
            st.error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def logout_user():
    """
    Clear authentication state
    """
    if 'token' in st.session_state:
        del st.session_state.token
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'username' in st.session_state:
        del st.session_state.username

def is_valid_email(email: str) -> bool:
    # Regular expression for validating an email
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_password(password: str) -> bool:
    # Check length
    if len(password) < 8:
        return False
    # Check for at least one numeral
    if not any(char.isdigit() for char in password):
        return False
    # Check for at least one special character
    if not any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/`~' for char in password):
        return False
    return True
