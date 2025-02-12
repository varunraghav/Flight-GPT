import requests
import streamlit as st

def get_api_response(question, session_id, model):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }  # Fixed closing brace

    data = {
        "question": question,
        "model": model
    }  # Fixed closing brace

    #if session_id:
    #    data["session_id"] = session_id

    try:
        response = requests.post(
            "http://localhost:8000/chat",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return response.json()
        st.error(f"API Error: {response.status_code}\n{response.text}")
        return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None
