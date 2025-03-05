# from fastapi import APIRouter, HTTPException
# import os
# import json 
# from typing import List, Dict
# from PyPDF2 import PdfReader
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from pymongo import MongoClient, ASCENDING, TEXT
# import certifi
# from pydantic import BaseModel

# router = APIRouter(prefix="/pdf-omar", tags=["PDF Omar Processing"])

# # Google Drive folder ID
# FOLDER_ID = "1bXUM5xHY5jJ4aGC6n9YjnC9uhPdzPBuE"

# # If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# # Initialize MongoDB client and embeddings
# try:
#     client = MongoClient(
#         os.getenv("MONGODB_ATLAS_CLUSTER_URI"),
#         tlsCAFile=certifi.where()
#     )
    
#     embeddings = GoogleGenerativeAIEmbeddings(
#         model="models/embedding-001",
#         google_api_key=os.getenv("GOOGLE_API_KEY")
#     )
    
#     # Setup MongoDB collections
#     db = client["capybara_db"]
#     collection = db["resumes_db"]
    
#     # Ensure indexes exist
#     collection.create_index([("text", TEXT)])
#     collection.create_index([("metadata.file_name", ASCENDING)])
    
# except Exception as e:
#     print(f"Initialization error: {e}")
#     raise e

# class ProcessingResponse(BaseModel):
#     total_files_processed: int
#     successful_files: List[str]
#     failed_files: List[Dict[str, str]]  # filename and error message
#     total_pages_processed: int

# def get_google_drive_service():
#     """Get Google Drive service using service account."""
#     try:
#         credentials = service_account.Credentials.from_service_account_file(
#             'credentials.json',
#             scopes=SCOPES
#         )
        
#         return build('drive', 'v3', credentials=credentials)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to initialize Drive service: {str(e)}"
#         )

# def split_text_into_chunks(text: str, chunk_size: int = 500) -> List[str]:
#     """
#     Split text into smaller chunks of a specified size.
#     Args:
#         text (str): The text to split.
#         chunk_size (int): Maximum number of characters per chunk.
#     Returns:
#         List[str]: List of text chunks.
#     """
#     chunks = []
#     for i in range(0, len(text), chunk_size):
#         chunks.append(text[i:i + chunk_size])
#     return chunks

# def extract_pdf_content(pdf_path: str, chunk_size: int = 500) -> Dict:
#     """
#     Extract text and metadata from PDF, split text into chunks, and structure the output.
#     Args:
#         pdf_path (str): Path to the PDF file.
#         chunk_size (int): Maximum number of characters per chunk.
#     Returns:
#         Dict: Structured metadata and content.
#     """
#     try:
#         with open(pdf_path, 'rb') as file:
#             pdf = PdfReader(file)
#             metadata = {
#                 "metadata_id": 1,  # You can generate a unique ID here
#                 "file_name": os.path.basename(pdf_path),
#                 "total_pages": len(pdf.pages),
#                 "source": "resume"
#             }
#             content = []
#             chunk_counter = 1  # To track chunk numbers across pages

#             for page_num in range(len(pdf.pages)):
#                 page = pdf.pages[page_num]
#                 text = page.extract_text()

#                 if text.strip():
#                     # Split the page text into smaller chunks
#                     chunks = split_text_into_chunks(text, chunk_size)

#                     for chunk_text in chunks:
#                         content.append({
#                             "page_num": page_num + 1,  # Page numbers start from 1
#                             "chunk_number": chunk_counter,
#                             "chunk_text": chunk_text
#                         })
#                         chunk_counter += 1  # Increment chunk counter

#             # Structure the result
#             result = {
#                 "metadata": metadata,
#                 "content": content
#             }

#             # Print the extracted content in JSON format
#             print("Extracted PDF Content (JSON Format):")
#             print(json.dumps(result, indent=4))  # Pretty-print JSON
#             return result

#     except Exception as e:
#         print(f"Error processing {pdf_path}: {str(e)}")
#         return {}



# @router.post("/process-cv-folder", response_model=ProcessingResponse)
# async def process_cv_folder():
#     """Process all PDFs in the cv folder."""
#     cv_folder = "app/cv"  # Folder at same level as main.py
    
#     if not os.path.exists(cv_folder):
#         raise HTTPException(
#             status_code=404,
#             detail=f"CV folder '{cv_folder}' not found!"
#         )
    
#     successful_files = []
#     failed_files = []
#     total_pages = 0
#     processed_count = 0
    
#     try:
#         # Clear existing collection
#         collection.delete_many({})
        
#         # Process each PDF in the cv folder
#         for filename in os.listdir(cv_folder):
#             if filename.endswith(".pdf"):
#                 pdf_path = os.path.join(cv_folder, filename)
#                 print(f"Processing {filename}...")
                
#                 try:
#                     # Extract content from the PDF
#                     result = extract_pdf_content(pdf_path)
                    
#                     if result:  # Check if result is not empty
#                         metadata = result["metadata"]
#                         content = result["content"]
                        
#                         # Process each chunk in the content
#                         for chunk in content:
#                             try:
#                                 # Generate embedding for the chunk text
#                                 embedding = embeddings.embed_query(chunk["chunk_text"])
                                
#                                 # Store document with embedding as a regular array
#                                 mongo_doc = {
#                                     "text": chunk["chunk_text"],
#                                     "metadata": metadata,
#                                     "chunk_number": chunk["chunk_number"],  # Add chunk_number
#                                     "page_number": chunk["page_num"],       # Add page_number
#                                     "embedding_array": embedding  # Store as regular array
#                                 }
                                
#                                 # Insert into MongoDB
#                                 collection.insert_one(mongo_doc)
#                                 processed_count += 1
#                                 print(f"Processed document {processed_count} from {filename}")
                                
#                             except Exception as e:
#                                 print(f"Error processing chunk from {filename}: {str(e)}")
#                                 continue
                        
#                         successful_files.append(filename)
#                         total_pages += len(content)  # Update total pages processed
                    
#                 except Exception as e:
#                     failed_files.append({
#                         "filename": filename,
#                         "error": str(e)
#                     })
#                     print(f"Error processing {filename}: {str(e)}")
        
#         return ProcessingResponse(
#             total_files_processed=len(successful_files) + len(failed_files),
#             successful_files=successful_files,
#             failed_files=failed_files,
#             total_pages_processed=total_pages
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/status")
# async def get_database_status():
#     """Get the current status of the resume database."""
#     try:
#         total_documents = collection.count_documents({})
#         unique_resumes = len(collection.distinct("metadata.file_name"))
        
#         return {
#             "total_documents": total_documents,
#             "unique_resumes": unique_resumes,
#             "status": "active"
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.delete("/clear-database")
# async def clear_database():
#     """Clear all documents from the database."""
#     try:
#         result = collection.delete_many({})
#         return {
#             "status": "success",
#             "documents_deleted": result.deleted_count,
#             "message": "Database cleared successfully"
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
import os
import re
import json
from typing import List, Dict
from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from pymongo import MongoClient, ASCENDING, TEXT
import certifi
from pydantic import BaseModel
from google.oauth2 import service_account
from googleapiclient.discovery import build
from io import BytesIO

router = APIRouter(prefix="/pdf-omar", tags=["PDF Omar Processing"])

# Google Drive folder ID
FOLDER_ID = "1kBeyHjaKLYQLamyzksjufmT4ox-7Ct4l"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    collection = db["resumes_db"]
    talents_collection = db["talents"]  # Collection to store unique talent names and IDs
    
    # Ensure indexes exist
    collection.create_index([("text", TEXT)])
    collection.create_index([("metadata.file_name", ASCENDING)])
    talents_collection.create_index([("talent_name", ASCENDING)], unique=True)  # Ensure talent names are unique
    
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

def split_text_into_chunks(text: str, chunk_size: int = 500) -> List[str]:
    """
    Split text into smaller chunks of a specified size.
    Args:
        text (str): The text to split.
        chunk_size (int): Maximum number of characters per chunk.
    Returns:
        List[str]: List of text chunks.
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

def extract_talent_name_with_gemini(text: str) -> str:
    """
    Extract the talent's name using Gemini API.
    Args:
        text (str): Extracted text from the PDF.
    Returns:
        str: Extracted and normalized talent name.
    """
    # Initialize Gemini model
    model = genai.GenerativeModel("gemini-pro")
    
    # Prompt Gemini to extract the talent's name
    prompt = (
        "Extract the full name of the person from the following resume text. "
        "Return only the full name in the format 'First Name Last Name'. "
        "If the name cannot be determined, return 'Unknown'.\n\n"
        f"Resume Text:\n{text}"
    )
    
    try:
        response = model.generate_content(prompt)
        talent_name = response.text.strip()
        
        # Normalize the talent name
        talent_name = re.sub(r"[^a-zA-Z0-9\s]", "", talent_name).lower()
        return talent_name
    except Exception as e:
        print(f"Error extracting name with Gemini: {str(e)}")
        return "unknown"

def get_or_create_talent_id(talent_name: str) -> int:
    """
    Get or create a unique talent_id for the given talent name.
    Args:
        talent_name (str): The talent's name.
    Returns:
        int: Unique talent_id.
    """
    # Normalize the talent name
    talent_name = re.sub(r"[^a-zA-Z0-9\s]", "", talent_name).lower()
    
    # Check if the talent name already exists
    talent = talents_collection.find_one({"talent_name": talent_name})
    
    if talent:
        return talent["talent_id"]
    else:
        # Generate a new talent_id (auto-increment)
        last_talent = talents_collection.find_one(sort=[("talent_id", -1)])
        new_talent_id = 1 if not last_talent else last_talent["talent_id"] + 1
        
        # Insert the new talent into the collection
        talents_collection.insert_one({
            "talent_id": new_talent_id,
            "talent_name": talent_name
        })
        
        return new_talent_id

def extract_pdf_content(pdf_bytes: bytes, filename: str, chunk_size: int = 500) -> Dict:
    """
    Extract text and metadata from PDF, split text into chunks, and structure the output.
    Args:
        pdf_bytes (bytes): PDF file content as bytes.
        filename (str): Name of the PDF file.
        chunk_size (int): Maximum number of characters per chunk.
    Returns:
        Dict: Structured metadata and content.
    """
    try:
        pdf = PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

        # Extract talent name using Gemini API
        talent_name = extract_talent_name_with_gemini(text)
        talent_id = get_or_create_talent_id(talent_name)
        
        metadata = {
            "metadata_id": 1,  # You can generate a unique ID here
            "file_name": filename,
            "total_pages": len(pdf.pages),
            "source": "resume",
            "talent_id": talent_id,  # Add talent_id to metadata
            "talent_name": talent_name  # Add talent_name to metadata
        }
        content = []
        chunk_counter = 1  # To track chunk numbers across pages

        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()

            if text.strip():
                # Split the page text into smaller chunks
                chunks = split_text_into_chunks(text, chunk_size)

                for chunk_text in chunks:
                    content.append({
                        "page_num": page_num + 1,  # Page numbers start from 1
                        "chunk_number": chunk_counter,
                        "chunk_text": chunk_text
                    })
                    chunk_counter += 1  # Increment chunk counter

        # Structure the result
        result = {
            "metadata": metadata,
            "content": content
        }

        # Print the extracted content in JSON format
        print("Extracted PDF Content (JSON Format):")
        print(json.dumps(result, indent=4))  # Pretty-print JSON
        return result

    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return {}

@router.post("/process-cv-folder", response_model=ProcessingResponse)
async def process_cv_folder():
    """Process all PDFs in the Google Drive folder."""
    successful_files = []
    failed_files = []
    total_pages = 0
    processed_count = 0
    
    try:
        # Clear existing collection
        collection.delete_many({})
        
        # Get Google Drive service
        drive_service = get_google_drive_service()
        
        # List files in the Google Drive folder
        results = drive_service.files().list(
            q=f"'{FOLDER_ID}' in parents",
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            raise HTTPException(
                status_code=404,
                detail="No files found in the specified Google Drive folder."
            )
        
        # Process each PDF in the Google Drive folder
        for item in items:
            if item['name'].endswith('.pdf'):
                file_id = item['id']
                filename = item['name']
                print(f"Processing {filename}...")
                
                try:
                    # Check if the file has already been processed
                    existing_doc = collection.find_one({"metadata.file_name": filename})
                    if existing_doc:
                        print(f"File {filename} already processed. Skipping...")
                        successful_files.append(filename)
                        continue
                    
                    # Download the PDF file
                    request = drive_service.files().get_media(fileId=file_id)
                    pdf_bytes = request.execute()
                    
                    # Extract content from the PDF
                    result = extract_pdf_content(pdf_bytes, filename)
                    
                    if result:  # Check if result is not empty
                        metadata = result["metadata"]
                        content = result["content"]
                        
                        # Process each chunk in the content
                        for chunk in content:
                            try:
                                # Generate embedding for the chunk text
                                embedding = embeddings.embed_query(chunk["chunk_text"])
                                
                                # Store document with embedding as a regular array
                                mongo_doc = {
                                    "text": chunk["chunk_text"],
                                    "metadata": metadata,
                                    "chunk_number": chunk["chunk_number"],  # Add chunk_number
                                    "page_number": chunk["page_num"],       # Add page_number
                                    "embedding_array": embedding  # Store as regular array
                                }
                                
                                # Insert into MongoDB
                                collection.insert_one(mongo_doc)
                                processed_count += 1
                                print(f"Processed document {processed_count} from {filename}")
                                
                            except Exception as e:
                                print(f"Error processing chunk from {filename}: {str(e)}")
                                continue
                        
                        successful_files.append(filename)
                        total_pages += len(content)  # Update total pages processed
                    
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