from fastapi import APIRouter, HTTPException
import os
import io
import json 
from typing import List, Dict
from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pymongo import MongoClient, ASCENDING, TEXT
import certifi
from pydantic import BaseModel
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

router = APIRouter(prefix="/pdf", tags=["PDF Processing"])

# Google Drive folder ID
FOLDER_ID = "1kBeyHjaKLYQLamyzksjufmT4ox-7Ct4l"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Initialize MongoDB client and embeddings
try:
    client = MongoClient(
        os.getenv("MONGODB_ATLAS_CLUSTER_URI"),
        tlsCAFile=certifi.where()
    )
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Setup MongoDB collections
    db = client["capybara_db"]
    collection = db["resumes"]
    
    # Ensure indexes exist
    collection.create_index([("text", TEXT)])
    collection.create_index([("metadata.file_name", ASCENDING)])
    
except Exception as e:
    print(f"Initialization error: {e}")
    raise e

class ProcessingResponse(BaseModel):
    total_files_processed: int
    successful_files: List[str]
    failed_files: List[Dict[str, str]]  # filename and error message
    total_pages_processed: int
    
def get_google_drive_service():
    """Get Google Drive service using service account."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'service_account.json',
            scopes=SCOPES
        )
        
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Drive service: {str(e)}"
        )

def extract_pdf_content(pdf_bytes: bytes, filename: str) -> List[Dict]:
    """Extract text and metadata from PDF bytes."""
    try:
        pdf = PdfReader(io.BytesIO(pdf_bytes))
        documents = []
        
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if text.strip():
                metadata = {
                    "file_name": filename,
                    "page_number": page_num + 1,
                    "total_pages": len(pdf.pages),
                    "source": "resume"
                }
                
                documents.append({
                    "text": text,
                    "metadata": metadata
                })
        
        return documents
    
    except Exception as e:
        raise Exception(f"Error processing {filename}: {str(e)}")
    
@router.post("/process-drive-folder", response_model=ProcessingResponse)
async def process_drive_folder():
    """Process all PDFs from the specified Google Drive folder."""
    successful_files = []
    failed_files = []
    total_pages = 0
    
    try:
        # Clear existing collection
        collection.delete_many({})
        
        # Initialize Google Drive service
        service = get_google_drive_service()
        
        # Verify folder exists
        try:
            folder = service.files().get(fileId=FOLDER_ID).execute()
            if folder.get('mimeType') != 'application/vnd.google-apps.folder':
                raise HTTPException(
                    status_code=400,
                    detail=f"ID {FOLDER_ID} is not a folder"
                )
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Folder not found or not accessible: {str(e)}"
            )
        
        # Get all PDF files
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf'",
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            return ProcessingResponse(
                total_files_processed=0,
                successful_files=[],
                failed_files=[],
                total_pages_processed=0
            )
        
        # Process each file
        for file in files:
            try:
                print(f"Processing {file['name']}...")
                
                request = service.files().get_media(fileId=file['id'])
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%")
                
                documents = extract_pdf_content(file_content.getvalue(), file['name'])
                
                for doc in documents:
                    try:
                        embedding = embeddings.embed_query(doc["text"])
                        
                        mongo_doc = {
                            "text": doc["text"],
                            "metadata": doc["metadata"],
                            "embedding_array": embedding
                        }
                        
                        collection.insert_one(mongo_doc)
                        total_pages += 1
                        
                    except Exception as e:
                        print(f"Error processing page in {file['name']}: {str(e)}")
                        continue
                
                successful_files.append(file['name'])
                
            except Exception as e:
                failed_files.append({
                    "filename": file['name'],
                    "error": str(e)
                })
                print(f"Error processing {file['name']}: {str(e)}")
        
        return ProcessingResponse(
            total_files_processed=len(successful_files) + len(failed_files),
            successful_files=successful_files,
            failed_files=failed_files,
            total_pages_processed=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

def extract_pdf_content_local(pdf_path: str) -> List[Dict]:
    """Extract text and metadata from PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf = PdfReader(file)
            documents = []
            
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if text.strip():
                    metadata = {
                        "file_name": os.path.basename(pdf_path),
                        "page_number": page_num + 1,
                        "total_pages": len(pdf.pages),
                        "source": "resume"
                    }
                    
                    documents.append({
                        "text": text,
                        "metadata": metadata
                    })
            
            return documents
    
    except Exception as e:
        raise Exception(f"Error processing {pdf_path}: {str(e)}")

@router.post("/process-cv-folder", response_model=ProcessingResponse)
async def process_cv_folder():
    """Process all PDFs in the cv folder."""
    cv_folder = "app/cv"  # Folder at same level as main.py
    
    if not os.path.exists(cv_folder):
        raise HTTPException(
            status_code=404,
            detail=f"CV folder '{cv_folder}' not found!"
        )
    
    successful_files = []
    failed_files = []
    total_pages = 0
    
    try:
        # Clear existing collection
        collection.delete_many({})
        
        # Process each PDF in the cv folder
        for filename in os.listdir(cv_folder):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(cv_folder, filename)
                
                try:
                    print(f"Processing {filename}...")
                    documents = extract_pdf_content_local(pdf_path)
                    
                    # Generate embeddings and store documents
                    for doc in documents:
                        try:
                            embedding = embeddings.embed_query(doc["text"])
                            
                            mongo_doc = {
                                "text": doc["text"],
                                "metadata": doc["metadata"],
                                "embedding_array": embedding
                            }
                            
                            # Insert into MongoDB
                            collection.insert_one(mongo_doc)
                            total_pages += 1
                            
                        except Exception as e:
                            print(f"Error processing page in {filename}: {str(e)}")
                            continue
                    
                    successful_files.append(filename)
                    
                except Exception as e:
                    failed_files.append({
                        "filename": filename,
                        "error": str(e)
                    })
                    print(f"Error processing {filename}: {str(e)}")
        
        return ProcessingResponse(
            total_files_processed=len(successful_files) + len(failed_files),
            successful_files=successful_files,
            failed_files=failed_files,
            total_pages_processed=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/status")
async def get_database_status():
    """Get the current status of the resume database."""
    try:
        total_documents = collection.count_documents({})
        unique_resumes = len(collection.distinct("metadata.file_name"))
        
        return {
            "total_documents": total_documents,
            "unique_resumes": unique_resumes,
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear-database")
async def clear_database():
    """Clear all documents from the database."""
    try:
        result = collection.delete_many({})
        return {
            "status": "success",
            "documents_deleted": result.deleted_count,
            "message": "Database cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))