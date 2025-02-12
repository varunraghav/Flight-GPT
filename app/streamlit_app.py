import streamlit as st
import uuid  # Add this import
#from sidebar import display_sidebar
#from chat_interface import display_chat_interface
#from login import handle_auth

#import streamlit as st
from chat_interface import display_chat_interface
from login import show_login_page
from sidebar import display_sidebar
# Page configuration
st.set_page_config(
    page_title="Airline Policy Assistant",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state variables
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



# Remove or comment out the extra multiline string to resolve the issue
# """  <-- This is causing Streamlit to render it on the UI
# Session state initialization
# required_session_keys = { 
#     'messages': [],
#     'session_id': None,
#     'authenticated': False,
#     'username': None,
#     'model': "gpt-4o-mini" 
# }
# for key, default in required_session_keys.items():
#     if key not in st.session_state:
#         st.session_state[key] = default

# Main app structure
# def main():
#     st.title("✈️ Airline Policy Analysis Assistant")
#     handle_auth() # Authentication handling
#     display_chat_interface()
#     if st.session_state.authenticated:
#         display_sidebar()
# if __name__ == "__main__":
#     main()
# """