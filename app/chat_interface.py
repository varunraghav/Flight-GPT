import streamlit as st
from api_utils import get_api_response

def display_chat_interface():
    st.markdown("""
    <style>
        .stChatInput {position: fixed; bottom: 20px; width: 70%;}
        div[data-testid="stVerticalBlock"] > div:has-textarea {position: fixed;}
    </style>
    """, unsafe_allow_html=True)

    # Initialize messages if not present
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me about airline policies!"}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Enter your policy question:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Analyzing policies..."):
            response = get_api_response(
                prompt,
                st.session_state.session_id,
                st.session_state.model
            )

        if response:
            # Update session ID if new
            st.session_state.session_id = response.get('session_id', st.session_state.session_id)
            
            # Display response
            with st.chat_message("assistant"):
                st.markdown(response['answer'])
                with st.expander("Response Details"):
                    st.caption(f"**Model**: {response['model']}")
                    st.caption(f"**Session ID**: `{response['session_id']}`")
                    st.code(response['answer'], language='markdown')

            st.session_state.messages.append({
                "role": "assistant",
                "content": response['answer']
            })