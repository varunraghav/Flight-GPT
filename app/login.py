import streamlit as st
from auth_utils import verify_password, create_user, hash_password

def show_login_page():
    st.title("Welcome to Airline Policy Assistant")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.header("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if verify_password(login_username, login_password):
                st.session_state.authenticated = True
                st.session_state.username = login_username
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.header("Sign Up")
        signup_username = st.text_input("Username", key="signup_username")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up"):
            if signup_password != confirm_password:
                st.error("Passwords do not match")
            elif not signup_username or not signup_password:
                st.error("Please fill in all fields")
            else:
                if create_user(signup_username, hash_password(signup_password)):
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Username already exists")




#import streamlit as st
#from auth_utils import show_login_form, hash_password, show_signup_form

#def handle_auth():
#    if st.session_state.get('authenticated'):
#        with st.sidebar:
#            st.header(f"Logged in as {st.session_state.username}")
#            if st.button("Logout"):
#                st.session_state.authenticated = False
#                st.session_state.username = None
#                st.rerun()
#    else:
#        tab1, tab2 = st.sidebar.tabs(["Login", "Sign Up"])
#        with tab1:
#            show_login_form()
#        with tab2:
#            show_signup_form()
