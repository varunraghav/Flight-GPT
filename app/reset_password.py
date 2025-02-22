# reset_password.py
import streamlit as st
import requests

def show_reset_password():
    # Initialize session state variables if not already set
    if "reset_email" not in st.session_state:
        st.session_state.reset_email = None
    if "otp_sent" not in st.session_state:
        st.session_state.otp_sent = False  # Tracks whether the OTP has been sent
    if "show_reset_password" not in st.session_state:
        st.session_state.show_reset_password = False

    st.header("Reset Password")

    # Add a "Go Back" button (returns user to Login/Sign Up page)
    if st.button("Go Back"):
        st.session_state.reset_email = None  # Clear reset email
        st.session_state.otp_sent = False  # Reset OTP sent state
        st.session_state.show_reset_password = False  # Reset session state
        st.rerun()  # Return to the default login page

    if not st.session_state.reset_email:
        # Input field for email and logic for sending OTP
        email = st.text_input("Enter your registered email address", key="reset_email_input")
        if st.button("Send OTP"):
            if not email:
                st.error("Please enter your email address")
            else:
                try:
                    # Call backend to verify email and send OTP
                    response = requests.post("http://localhost:8000/verify-email", json={"email": email})
                    if response.status_code == 200:
                        # If email exists, send OTP
                        otp_response = requests.post("http://localhost:8000/request-password-reset", json={"email": email})
                        if otp_response.status_code == 200:
                            st.session_state.reset_email = email
                            st.session_state.otp_sent = True  # Mark OTP as sent
                            st.success("OTP sent to your email. Please check your inbox.")
                        else:
                            st.error("Failed to send OTP. Please try again.")
                    else:
                        st.error("No such email exists in our records")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    if st.session_state.otp_sent:
        st.info(f"An OTP has been sent to {st.session_state.reset_email}")

        # Input fields for OTP, New Password, and Confirm Password
        otp = st.text_input("Enter OTP", type="password", key="otp_input")
        new_password = st.text_input("New Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password")

        if st.button("Reset Password"):
            if not otp or not new_password or not confirm_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                try:
                    # Call backend to verify OTP and reset password
                    response = requests.post(
                        "http://localhost:8000/verify-reset-password",
                        json={"email": st.session_state.reset_email, "otp": otp, "new_password": new_password}
                    )
                    if response.status_code == 200:
                        st.success("Password reset successful! Please log in with your new credentials.")
                        st.session_state.reset_email = None  # Clear email from session state
                        st.session_state.show_reset_password = False  # Reset view state
                        st.session_state.otp_sent = False
                        st.rerun()  # Redirect back to login
                    else:
                        st.error("Invalid OTP or OTP has expired")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
