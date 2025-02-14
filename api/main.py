import sqlite3
import traceback
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi import FastAPI
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from pydantic_models import QueryResponse
from llamaindex_utils import initialize_system
from db_utils import get_db_connection
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