from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
import os
import certifi
from typing import List, Dict

router = APIRouter(prefix="/rag", tags=["Team Assembly"])

# Initialize clients and models
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

@router.get("/assemble-team")
async def assemble_team(project_requirements: str):
    try:
        if not project_requirements:
            raise HTTPException(
                status_code=400, 
                detail="Project requirements are required"
            )
        
        relevant_resumes = find_similar_resumes(project_requirements)
        
        context = "\n\nAvailable Candidates:\n"
        for resume in relevant_resumes:
            context += f"Candidate from {resume['metadata']['file_name']}:\n{resume['text']}\n\n"
        
        prompt = f"{SYSTEM_PROMPT}\n\nProject Requirements:\n{project_requirements}\n{context}"
        response = llm.predict(prompt)
        
        return {
            "project_requirements": project_requirements,
            "team_recommendation": response,
            "sources": [
                {
                    "file_name": resume["metadata"]["file_name"],
                    "page_number": resume["metadata"]["page_number"]
                }
                for resume in relevant_resumes
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))