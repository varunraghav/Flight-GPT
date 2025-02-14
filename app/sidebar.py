import streamlit as st

def display_sidebar():
    with st.sidebar:
        st.title("Settings")
        
        # Model selection - just use key to automatically store in session state
        st.selectbox(
            "Select Model",
            ["gpt-4o-mini", "gpt-4"],
            key="model"  # This automatically creates st.session_state.model
        )
        
        if st.session_state.authenticated:
            st.write(f"Logged in as: {st.session_state.username}")
            
            if "session_id" in st.session_state:
                st.write(f"Session ID: {st.session_state.session_id}")
            
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.rerun()
