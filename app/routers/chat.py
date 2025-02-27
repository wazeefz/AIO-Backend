import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from datetime import datetime
from ..database import get_db
import certifi
from ..models.chat import Chat, Message
from ..schemas.chat import ChatResponse, ChatListResponse, MessageResponse, MessageCreate   

try:
    client = MongoClient(
        os.getenv("MONGODB_ATLAS_CLUSTER_URI"),
        tlsCAFile=certifi.where()
    )
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7
    )
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
except Exception as e:
    print(f"Initialization error: {e}")
    raise e

SYSTEM_PROMPT = """
[Your existing system prompt here]
"""

def find_similar_resumes(query: str, limit: int = 5) -> List[Dict]:
    """Find similar resumes using text search and embedding similarity."""
    collection = client["capybara_db"]["resumes"]
    
    query_embedding = embeddings.embed_query(query)
    
    results = collection.find(
        {"$text": {"$search": query}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(limit)
    
    return list(results)


router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/{user_id}", response_model=ChatResponse)
def create_chat(user_id: int, db: Session = Depends(get_db)):
    new_chat = Chat(user_id=user_id, title="New Chat")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@router.get("/{user_id}/{chat_id}", response_model=ChatResponse)
async def get_chat(user_id: int, chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.conversation_id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.get("/{user_id}", response_model=List[ChatListResponse])
def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    try:
        chats = db.query(Chat).filter(Chat.user_id == user_id)#.order_by(Chat.updated_at.desc()).all()
        if not chats:
            return []
        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(user_id: int, chat_id: int, db: Session = Depends(get_db)):
    try:
        chat = db.query(Chat).filter(Chat.conversation_id == chat_id, Chat.user_id == user_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        messages = db.query(Message).filter(Message.conversation_id == chat_id).order_by(Message.created_at).all()
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/{chat_id}/message", response_model=MessageResponse)
async def create_message(
    user_id: int, 
    chat_id: int, 
    message: MessageCreate, 
    db: Session = Depends(get_db)
):
    # Print received data for debugging
    print(f"Received message data: {message.dict()}")
    
    chat = db.query(Chat).filter(
        Chat.conversation_id == chat_id, 
        Chat.user_id == user_id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    new_message = Message(
        conversation_id=chat_id,
        message_text=message.message_text,
        sender=message.sender
    )
    
    try:
        db.add(new_message)
        if message.sender == "user" and len(chat.messages) == 0:
            chat.title = (
                message.message_text[:30] + "..." 
                if len(message.message_text) > 30 
                else message.message_text
            )
        
        db.commit()
        db.refresh(new_message)
        return new_message
    except Exception as e:
        print(f"Error creating message: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# @router.get("/ask-question/")
# async def ask_question(question: str = Query(..., description="Your question")):
#     try:
#         response = llm_model.invoke(question)
#         return {
#             "content": response.content if hasattr(response, 'content') else str(response)
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/ask-question/")
async def ask_question(
    question: str = Query(..., description="Your question or project requirements"),
    is_team_assembly: bool = Query(True, description="Set to True for team assembly requests")
):
    try:
        if is_team_assembly:
            # Team assembly logic (from assemble-team endpoint)
            if not question:
                raise HTTPException(
                    status_code=400, 
                    detail="Project requirements are required for team assembly"
                )
            
            # Find relevant resumes
            relevant_resumes = find_similar_resumes(question)
            
            # Build context for the prompt
            context = "\n\nAvailable Candidates:\n"
            for resume in relevant_resumes:
                context += f"Candidate from {resume['metadata']['file_name']}:\n{resume['text']}\n\n"
            
            # Create the prompt for the LLM
            prompt = f"{SYSTEM_PROMPT}\n\nProject Requirements:\n{question}\n{context}"
            
            # Get the response from the LLM
            response = llm.predict(prompt)
            
            # Return the team assembly response
            return {
                "type": "team_assembly",
                "project_requirements": question,
                "team_recommendation": response,
                "sources": [
                    {
                        "file_name": resume["metadata"]["file_name"],
                        "page_number": resume.get("page_number", "N/A")  # Use get to avoid KeyError
                    }
                    for resume in relevant_resumes
                ]
            }
        else:
            # General question logic with RAG
            # Step 1: Retrieve relevant documents from MongoDB using vector search
            collection = client["capybara_db"]["resumes"]
            
            # Generate embedding for the question
            query_embedding = embeddings.embed_query(question)
            
            # Perform vector search
            results = collection.aggregate([
                {
                    "$vectorSearch": {
                        "index": "vector_index",  # Replace with your vector index name
                        "path": "embedding_array",  # Field containing the embeddings
                        "queryVector": query_embedding,
                        "numCandidates": 10,  # Number of candidates to retrieve
                        "limit": 5  # Number of results to return
                    }
                },
                {
                    "$project": {
                        "text": 1,
                        "metadata": 1,
                        "score": { "$meta": "vectorSearchScore" }
                    }
                }
            ])
            
            # Convert results to a list
            relevant_documents = list(results)
            
            # Step 2: Build context for the prompt
            context = "\n\nRelevant Documents:\n"
            for doc in relevant_documents:
                context += f"Document: {doc['metadata']['file_name']}\n{doc['text']}\n\n"
            
            # Step 3: Create the prompt for the LLM
            prompt = f"{SYSTEM_PROMPT}\n\nQuestion:\n{question}\n{context}"
            
            # Step 4: Get the response from the LLM
            response = llm.predict(prompt)
            
            # Step 5: Return the response
            return {
                "type": "general_question",
                "content": response,
                "sources": [
                    {
                        "file_name": doc["metadata"]["file_name"],
                        "page_number": doc.get("page_number", "N/A")  # Use get to avoid KeyError
                    }
                    for doc in relevant_documents
                ]
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{user_id}/{chat_id}", )
async def delete_chat(
    user_id: int,
    chat_id: int,
    db: Session = Depends(get_db)
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