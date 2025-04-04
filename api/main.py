import sqlite3
import traceback
import random
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi import FastAPI
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from pydantic_models import QueryResponse
from llamaindex_utils import initialize_system
from db_utils import get_db_connection
from email_utils import send_otp_email
from auth_utils import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
app = FastAPI()
agent = initialize_system()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://flightgpt.streamlit.app"],  # Allow Streamlit Cloud app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add this Pydantic model at the top
class ChatQuery(BaseModel):
    question: str
    model: str
    session_id: Optional[str] = None


# Dictionary to track message count per session
message_count = {}

@app.post("/direct_chat", response_model=QueryResponse)
async def chat(query_input: ChatQuery):
    try:
        # Add validation
        if not query_input.question:
            raise HTTPException(status_code=400, detail="Question is required")

        # Track message count per session
        session_id = query_input.session_id or str(uuid.uuid4())
        if session_id not in message_count:
            message_count[session_id] = 0

        if message_count[session_id] >= 5:
            raise HTTPException(status_code=403, detail="Message limit reached. Please login to continue.")

        # Existing logic with explicit initialization
        if not hasattr(app.state, 'agent'):
            app.state.agent = initialize_system()

        # Process through agent
        response = app.state.agent.chat(query_input.question)

        # Increment message count
        message_count[session_id] += 1

        # Your existing logging/DB logic
        return QueryResponse(
            answer=str(response),
            session_id=session_id,
            model=query_input.model
        )
    except Exception as e:
        logging.error(f"Chat error: {traceback.format_exc()}")
        raise HTTPException(500, detail=str(e))

# Update the chat endpoint
# Protect your chat endpoint
@app.post("/chat", response_model=QueryResponse)
async def chat(
    query_input: ChatQuery,
    current_user: str = Depends(get_current_user)
):
    try:
        # Add validation
        if not query_input.question:
            raise HTTPException(status_code=400, detail="Question is required")
            
        # Existing logic with explicit initialization
        if not hasattr(app.state, 'agent'):
            app.state.agent = initialize_system()
            
        # Process through agent
        response = app.state.agent.chat(query_input.question)
        
        # Your existing logging/DB logic
        return QueryResponse(
            answer=str(response),
            session_id=query_input.session_id or str(uuid.uuid4()),
            model=query_input.model
        )
    except Exception as e:
        logging.error(f"Chat error: {traceback.format_exc()}")
        raise HTTPException(500, detail=str(e))


# Add new endpoint
@app.post("/verify-user")
def verify_user_credentials(user_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (user_data['username'],))
    result = cursor.fetchone()
    conn.close()
    
    valid = False
    if result and result[0] == user_data['password_hash']:
        valid = True
    return {"valid": valid}


@app.post("/create-user")
def create_user(user_data: dict):
    conn = get_db_connection()
    try:
        hashed_password = get_password_hash(user_data['password'])
        conn.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (user_data['username'], hashed_password)
        )
        conn.commit()
        return {"message": "User created successfully!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()



# Add these new endpoints
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/verify-email")
async def verify_email(data: dict):
    email = data.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if email exists in users table
    cursor.execute('SELECT id FROM users WHERE username = ?', (email,))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {"message": "Email verified"}

@app.post("/request-password-reset")
async def request_password_reset(data: dict):
    email = data.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user ID (email existence already verified)
    cursor.execute('SELECT id FROM users WHERE username = ?', (email,))
    user = cursor.fetchone()
    
    # Generate OTP and set expiry
    otp = ''.join(random.choices('0123456789', k=6))
    expiry = datetime.utcnow() + timedelta(minutes=10)
    
    # Store OTP in database
    cursor.execute(
        '''INSERT INTO password_reset_tokens (user_id, otp, expiry, used)
           VALUES (?, ?, ?, 0)''', 
        (user['id'], otp, expiry)
    )
    conn.commit()

    print(f"Email is {email}")
    print(f"OTP is {otp}")
    
    # Send OTP via email
    if not send_otp_email(email, otp):
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    
    return {"message": "OTP sent successfully"}

@app.post("/verify-reset-password")
async def verify_reset_password(data: dict):
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user ID
    cursor.execute('SELECT id FROM users WHERE username = ?', (email,))
    user = cursor.fetchone()
    
    # Verify OTP
    cursor.execute(
        '''SELECT id FROM password_reset_tokens 
           WHERE user_id = ? AND otp = ? AND used = 0 AND expiry > ?''', 
        (user['id'], otp, datetime.utcnow())
    )
    token = cursor.fetchone()
    
    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # Update password
    hashed_password = get_password_hash(new_password)
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                  (hashed_password, user['id']))
    
    # Mark OTP as used
    cursor.execute('UPDATE password_reset_tokens SET used = 1 WHERE id = ?', 
                  (token['id'],))
    
    conn.commit()
    return {"message": "Password reset successful"}