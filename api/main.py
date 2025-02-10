import sqlite3
import traceback
from typing import Optional
from fastapi import HTTPException
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_models import QueryInput, QueryResponse
from llamaindex_utils import initialize_system
from db_utils import insert_application_logs, get_chat_history
from db_utils import get_db_connection
from fastapi.middleware.cors import CORSMiddleware
import shutil
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
@app.post("/chat", response_model=QueryResponse)
def chat(query_input: ChatQuery):  # Changed from QueryInput
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
        conn.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (user_data['username'], user_data['password_hash'])
        )
        conn.commit()
        return {"message": "User created successfully!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()