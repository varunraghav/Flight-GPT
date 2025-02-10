import streamlit as st
from sidebar import display_sidebar
from chat_interface import display_chat_interface
from login import handle_auth

# Page configuration
st.set_page_config(
    page_title="Airline Policy Assistant",
    page_icon="✈️",
    layout="wide"
)

# Session state initialization
required_session_keys = {
    'messages': [],
    'session_id': None,
    'authenticated': False,
    'username': None,
    'model': "gpt-4o-mini"
}

for key, default in required_session_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Main app structure
def main():
    st.title("✈️ Airline Policy Analysis Assistant")
    handle_auth()  # Authentication handling
    display_chat_interface()
    
    if st.session_state.authenticated:
        display_sidebar()

if __name__ == "__main__":
    main()
