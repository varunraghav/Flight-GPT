import streamlit as st

def display_sidebar():
    if not st.session_state.get('authenticated'):
        st.sidebar.info("Please log in to access premium features")
        return

    # Model selection only
    model_options = ["gpt-4o-mini", "gpt-4"]
    st.sidebar.selectbox(
        "Select AI Model",
        options=model_options,
        key="model",
        help="Choose between different GPT-4 model variants"
    )
    
    # System info section
    st.sidebar.markdown("---")
    st.sidebar.subheader("Session Information")
    if st.session_state.session_id:
        st.sidebar.caption(f"Session ID: `{st.session_state.session_id}`")
