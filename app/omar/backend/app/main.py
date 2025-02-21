import os
import glob
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from . import database, schemas 
from .models import User, Department, Chat, Message

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Medical PDF QA System with Chat")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configurations
SECRET_KEY = "your-secret-key-here"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Load environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_ATLAS_CLUSTER_URI = os.getenv("MONGODB_ATLAS_CLUSTER_URI")

# Initialize MongoDB client
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)

# Define database and collection names
DB_NAME = "test_db"
COLLECTION_NAME = "test_collection_pdf"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "text-index-pdf"

# Get MongoDB collection
MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]
MONGODB_COLLECTION.delete_many({})

# Initialize Google Generative AI model and embeddings
llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_API_KEY)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)

# Initialize MongoDB Atlas Vector Search
vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create Vector Search Index
def create_vector_search_index():
    try:
        vector_store.create_vector_search_index(dimensions=768)
        print("Vector Search Index Created!")
    except Exception as e:
        print(f"Vector Search Index already exists or error: {str(e)}")

# Load and Store Documents
def load_and_store_documents(pdf_dir="pdf_files/"):
    try:
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_files = glob.glob(f"{pdf_dir}/*.pdf")
        
        if not pdf_files:
            print("No PDF files found in the directory.")
            return
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file}")
            try:
                loader = PyPDFLoader(pdf_file)
                docs = loader.load_and_split(text_splitter)
                
                for doc in docs:
                    doc.metadata["source_file"] = os.path.basename(pdf_file)
                
                vector_store.add_documents(docs)
                print(f"Added {len(docs)} chunks from {pdf_file}")
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
        
        print("All documents processed and added to Vector Store!")
    except Exception as e:
        print(f"Error loading or storing documents: {str(e)}")

@app.post("/signup/")
async def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if email already exists
    print("checkpoint1")
    existing_user = db.query(User).filter(User.email == user.email).first()
    print("checkpoint2")
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    try:
        # Hash the password
        hashed_password = pwd_context.hash(user.password)
        
        # Create new user object
        db_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            department_id=user.department_id,
            role=user.role
        )
        
        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {"message": "User created successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating user: {str(e)}"
        )

@app.post("/login/", response_model=schemas.Token)
async def login(login_request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == login_request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name
    }

@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(database.get_db)
):
    # Find the user in the database
    db_user = db.query(User).filter(User.user_id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if email is being updated and if it's already taken
    if user_update.email and user_update.email != db_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    try:
        # Update user fields if they are provided
        if user_update.name is not None:
            db_user.name = user_update.name
        
        if user_update.email is not None:
            db_user.email = user_update.email
            
        if user_update.password is not None:
            db_user.password = pwd_context.hash(user_update.password)
            
        if user_update.department_id is not None:
            # Optionally verify that the department exists
            # department = db.query(Department).filter(
            #     Department.department_id == user_update.department_id
            # ).first()
            # if not department:
            #     raise HTTPException(
            #         status_code=404,
            #         detail="Department not found"
            #     )
            db_user.department_id = user_update.department_id
            
        if user_update.role is not None:
            db_user.role = user_update.role
        
        # Commit the changes to the database
        db.commit()
        db.refresh(db_user)
        
        # Return the updated user information
        return {
            "message": "User updated successfully",
            "user": {
                "user_id": db_user.user_id,
                "name": db_user.name,
                "email": db_user.email,
                "department_id": db_user.department_id,
                "role": db_user.role
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating user: {str(e)}"
        )
    
@app.get("/users/", response_model=List[schemas.UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving users: {str(e)}"
        )

# Get specific user by ID endpoint
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: Session = Depends(database.get_db)):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        print("checkpoint4")
        return user
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user: {str(e)}"
        )

# PDF Upload Endpoint
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_dir = "pdf_files"
        os.makedirs(pdf_dir, exist_ok=True)
        
        file_path = os.path.join(pdf_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        
        loader = PyPDFLoader(file_path)
        docs = loader.load_and_split(text_splitter)
        
        for doc in docs:
            doc.metadata["source_file"] = file.filename
        
        vector_store.add_documents(docs)
        
        return JSONResponse(content={
            "message": f"Successfully uploaded and processed {file.filename}",
            "chunks_processed": len(docs)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# List PDFs Endpoint
@app.get("/list-pdfs/")
async def list_pdfs():
    try:
        pipeline = [
            {"$group": {"_id": "$metadata.source_file"}},
            {"$match": {"_id": {"$ne": None}}},
            {"$project": {"filename": "$_id", "_id": 0}}
        ]
        
        result = list(MONGODB_COLLECTION.aggregate(pipeline))
        return {"pdfs": [doc["filename"] for doc in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing PDFs: {str(e)}")

# Ask Question Endpoint
@app.get("/ask-question/")
async def ask_question(
    question: str = Query(..., description="Your question"),
    pdf_file: str = Query(None, description="Optional: Specific PDF to search in")
):
    try:
        search_kwargs = {}
        if pdf_file:
            search_kwargs = {
                "filter": {"metadata.source_file": pdf_file}
            }
        
        retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
        
        chain = RetrievalQA.from_chain_type(
            llm=llm_model,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=True
        )
        
        result = chain.invoke(question)
        
        sources = []
        if hasattr(result, 'get') and result.get('source_documents'):
            for doc in result['source_documents']:
                if 'source_file' in doc.metadata and doc.metadata['source_file'] not in sources:
                    sources.append(doc.metadata['source_file'])
        
        return {
            "question": question,
            "answer": result["result"],
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Chat Endpoints
@app.post("/chat/{user_id}", response_model=schemas.ChatResponse)
async def create_chat(
    user_id: int,
    db: Session = Depends(database.get_db)
):
    new_chat = Chat(user_id=user_id, title="New Chat")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@app.get("/chat/{user_id}/{chat_id}", response_model=schemas.ChatResponse)
async def get_chat(
    user_id: int,
    chat_id: int,
    db: Session = Depends(database.get_db)
):
    chat = db.query(Chat).filter(
        Chat.conversation_id == chat_id,
        Chat.user_id == user_id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@app.get("/chat/history/{user_id}", response_model=List[schemas.ChatResponse])
async def get_chat_history(
    user_id: int,
    db: Session = Depends(database.get_db)
):
    chats = db.query(Chat).filter(
        Chat.user_id == user_id
    ).order_by(Chat.updated_at.desc()).all()
    return chats

@app.post("/chat/{user_id}/{chat_id}/message", response_model=schemas.MessageResponse)
async def create_message(
    user_id: int,
    chat_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(database.get_db)
):
    chat = db.query(Chat).filter(
        Chat.conversation_id == chat_id,
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_message = Message(
        conversation_id=chat_id,
        content=message.content,
        role=message.role
    )
    db.add(new_message)

    if message.role == "user" and len(chat.messages) == 0:
        chat.title = message.content[:30] + "..." if len(message.content) > 30 else message.content

    chat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(new_message)
    return new_message

@app.delete("/chat/{user_id}/{chat_id}", response_model=schemas.ChatResponse)
async def delete_chat(
    user_id: int,
    chat_id: int,
    db: Session = Depends(database.get_db)
):
    chat = db.query(Chat).filter(
        Chat.conversation_id == chat_id,
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}

if __name__ == "__main__":
    create_vector_search_index()
    load_and_store_documents()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)