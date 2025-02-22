# email_utils.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your SendGrid API key - store this in environment variables
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')  # Your verified sender email in SendGrid

def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Send OTP email using SendGrid
    
    Args:
        to_email (str): Recipient's email address
        otp (str): Generated OTP
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create SendGrid client
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        
        # Create email components
        from_email = Email(SENDER_EMAIL)
        to_email = To(to_email)
        subject = "Password Reset OTP - Airline Assistant"
        
        # Create HTML content
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Password Reset Request</h2>
                <p>Hello,</p>
                <p>You have requested to reset your password for your Airline Assistant account.</p>
                <p>Your OTP is: <strong style="font-size: 20px; color: #4CAF50;">{otp}</strong></p>
                <p>This OTP will expire in 10 minutes (at {(datetime.now().strftime('%H:%M:%S'))})</p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <br>
                <p>Best regards,</p>
                <p>Airline Assistant Team</p>
            </body>
        </html>
        """
        
        content = Content("text/html", html_content)
        
        # Construct and send email
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        
        # Log success
        logger.info(f"Email sent successfully to {to_email}. Status code: {response.status_code}")
        return True
        
    except Exception as e:
        # Log error
        logger.error(f"Failed to send email to {to_email}. Error: {str(e)}")
        return False

def verify_sendgrid_connection() -> bool:
    """
    Verify SendGrid API key and connection
    
    Returns:
        bool: True if connection is valid, False otherwise
    """
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.client.mail.send.post(
            request_body={
                "personalizations": [{"to": [{"email": "test@example.com"}]}],
                "from": {"email": SENDER_EMAIL},
                "subject": "SendGrid API Test",
                "content": [{"type": "text/plain", "value": "Test content"}]
            }
        )
        return True
    except Exception as e:
        logger.error(f"SendGrid verification failed: {str(e)}")
        return False


# Initialize and verify SendGrid connection when module is loaded
if __name__ == "__main__":
    if not SENDGRID_API_KEY:
        logger.error("SendGrid API key not found in environment variables")
    else:
        if verify_sendgrid_connection():
            logger.info("SendGrid connection verified successfully")
        else:
            logger.error("Failed to verify SendGrid connection")
