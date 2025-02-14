import requests
import streamlit as st

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
