import streamlit as st
import uuid 
from chat_interface import display_chat_interface  # Importing a function to display the chat interface
from login import show_login_page  # Importing a function to show the login page
from sidebar import display_sidebar  # Importing a function to display the sidebar

# Page configuration
st.set_page_config(
    page_title="Airline Policy Assistant",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state variables
# Streamlit's session state is used to store variables that persist across user interactions.
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "session_id" not in st.session_state:  # Add this
    st.session_state.session_id = str(uuid.uuid4())  # Generate unique session ID

def main():
    # Always show sidebar for model selection etc.
    display_sidebar()
    
    if not st.session_state.authenticated:
        # Show login/signup page as main content when not authenticated
        show_login_page()
    else:
        # Show chat interface only after authentication
        display_chat_interface()

if __name__ == "__main__":
    main()
