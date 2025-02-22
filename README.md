# Airline Policy Chatbot (FlightGPT)

**Next-gen RAG system** for airline policy analysis with structured responses  

<img width="686" alt="Flowchart" src="https://github.com/user-attachments/assets/e07ac013-9e40-41cd-8a2a-9e82a8a6fa53" />

## 🔑 Key Features
- **Multi-Airline Policy Analysis**  
- JWT Protected API Endpoints  
- Structured Response Templates  
- Session-based Chat History  
- Hybrid Semantic Search (Vector + Metadata)  
- User Authentication System  

## 🛠️ Tech Stack
### **Frontend**  
`Streamlit` · `JWT` · `UUID Session Management`  

### **Backend**  
`FastAPI` · `LlamaIndex` · `ChromaDB` · `SQLite`  

### **AI Components**  
`gpt-4o-mini` · `BAAI/bge-base-en-v1.5` embeddings · RAG Architecture  

## 📁 Project Structure
```bash
flightgpt/
├── frontend/
│   ├── streamlit_app.py      # Main application
│   ├── api_utils.py          # API communication
│   ├── login.py              # Authentication UI
│   ├── chat_interface.py     # Chat interface
│   └── sidebar.py            # Sidebar controls
│
├── backend/
│   ├── main.py               # API server
│   ├── auth_utils.py         # Security framework
│   ├── llamaindex_utils.py   # AI orchestration
│   └── db_utils.py           # Database operations
```

## 🔒 Security Implementation
Password Hashing: bcrypt with 60k iterations
Token Security:
JWT_CONFIG = {
    "secret_key": "256-bit-encryption-key",
    "algorithm": "HS256",
    "expiry": timedelta(minutes=30)
}
CORS Restrictions
Input Validation Layers
Session Isolation

## 🚀 Getting Started
#### Requirements
Python 3.10+
#### ENV Variables:
OPENAI_API_KEY  
SECRET_KEY  
DATABASE_URL

### Installation
#### Backend
1. cd api
2. pip install -r requirements.txt
3. uvicorn main:app --reload

#### Frontend
1. cd app
2. pip install -r requirements.txt
3. streamlit run streamlit_app.py

⏳ Upcoming: Uploading Sample Database containing vector index









