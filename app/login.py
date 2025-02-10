import streamlit as st
from auth_utils import show_login_form, hash_password, show_signup_form

def handle_auth():
    if st.session_state.get('authenticated'):
        with st.sidebar:
            st.header(f"Logged in as {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.rerun()
    else:
        tab1, tab2 = st.sidebar.tabs(["Login", "Sign Up"])
        with tab1:
            show_login_form()
        with tab2:
            show_signup_form()