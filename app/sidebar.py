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



#import streamlit as st
#
#def display_sidebar():
#    if not st.session_state.get('authenticated'):
#        st.sidebar.info("Please log in to access premium features")
#        return
#
#    # Model selection only
#    model_options = ["gpt-4o-mini", "gpt-4"]
#    st.sidebar.selectbox(
#        "Select AI Model",
#        options=model_options,
#        key="model",
#        help="Choose between different GPT-4 model variants"
#    )
#    
#    # System info section
#    st.sidebar.markdown("---")
#    st.sidebar.subheader("Session Information")
#    if st.session_state.session_id:
#        st.sidebar.caption(f"Session ID: `{st.session_state.session_id}`")


