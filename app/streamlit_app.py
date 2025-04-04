import streamlit as st
import uuid 
from chat_interface import display_chat_interface  # Importing a function to display the chat interface
from login import show_login_page  # Importing a function to show the login page
from sidebar import display_sidebar  # Importing a function to display the sidebar
import streamlit.components.v1 as components
from right_sidebar import display_right_sidebar


# Page configuration
st.set_page_config(
    page_title="Airline Policy Assistant",
    page_icon="✈️",
    layout="wide"
)

# Add Google Analytics tracking code
GA_TRACKING_CODE = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-L9F1D0E5Y8"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-L9F1D0E5Y8');
</script>
"""
components.html(GA_TRACKING_CODE, height=0, width=0)

# Initialize session state variables
# Streamlit's session state is used to store variables that persist across user interactions.
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "session_id" not in st.session_state:  # Add this
    st.session_state.session_id = str(uuid.uuid4())  # Generate unique session ID

def main():
    # Create two-column layout
    left_col, right_col = st.columns([2.5, 1])
    
    with left_col:
        # Display main sidebar for model selection
        display_sidebar()
        
        if not st.session_state.authenticated:
            # Show login/signup page as main content
            show_login_page()
        else:
            # Show main chat interface after authentication
            display_chat_interface()
    
    with right_col:
        # Always show the right sidebar chat interface
        display_right_sidebar()

if __name__ == "__main__":
    main()
