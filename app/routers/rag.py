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
You are CapybarAI, a team assembly assistant. Your task is to:
1. Analyze the project requirements provided
2. Search through the resume database to find the best matching candidates
3. Recommend a team composition with clear justification for each selection
4. Consider factors like skills, experience, availability, and team dynamics
5. Present your recommendations in a structured format

Format your response exactly as follows:

Project Requirements Analysis:
[Provide a brief analysis of the key requirements and challenges]

Recommended Team:

1. [Full Name] - [Primary Role]
   Key Qualifications:
   - [Skill Name] (X years experience)
   - [Skill Name] (X years)
   - [Certification/Qualification]
   
   Justification:
   [Explain why this person is a good fit for the role]

2. [Full Name] - [Primary Role]
   Key Qualifications:
   - [List key relevant skills]
   - [List relevant experience]
   - [List relevant certifications]
   
   Justification:
   [Explain why this person is a good fit for the role]

[Continue for each team member...]

PS: Roles and Skills categories are in maximum two words only. 

Team Dynamics:
[Explain how the team members complement each other and why they would work well together]
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