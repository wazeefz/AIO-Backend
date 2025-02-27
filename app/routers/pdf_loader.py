from fastapi import APIRouter, HTTPException
import os
import json 
from typing import List, Dict
from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pymongo import MongoClient, ASCENDING, TEXT
import certifi
from pydantic import BaseModel

router = APIRouter(prefix="/pdf", tags=["PDF Processing"])

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

# def extract_pdf_content(pdf_path: str) -> List[Dict]:
#     """Extract text and metadata from PDF."""
#     try:
#         with open(pdf_path, 'rb') as file:
#             pdf = PdfReader(file)
#             documents = []
            
#             for page_num in range(len(pdf.pages)):
#                 page = pdf.pages[page_num]
#                 text = page.extract_text()
                
#                 if text.strip():
#                     metadata = {
#                         "file_name": os.path.basename(pdf_path),
#                         "page_number": page_num + 1,
#                         "total_pages": len(pdf.pages),
#                         "source": "resume"
#                     }
                    
#                     documents.append({
#                         "text": text,
#                         "metadata": metadata
#                     })
            
#             return documents
    
#     except Exception as e:
#         raise Exception(f"Error processing {pdf_path}: {str(e)}")

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

def extract_pdf_content(pdf_path: str, chunk_size: int = 500) -> Dict:
    """
    Extract text and metadata from PDF, split text into chunks, and structure the output.
    Args:
        pdf_path (str): Path to the PDF file.
        chunk_size (int): Maximum number of characters per chunk.
    Returns:
        Dict: Structured metadata and content.
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf = PdfReader(file)
            metadata = {
                "metadata_id": 1,  # You can generate a unique ID here
                "file_name": os.path.basename(pdf_path),
                "total_pages": len(pdf.pages),
                "source": "resume"
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
        print(f"Error processing {pdf_path}: {str(e)}")
        return {}

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
    
#     try:
#         # Clear existing collection
#         collection.delete_many({})
        
#         # Process each PDF in the cv folder
#         for filename in os.listdir(cv_folder):
#             if filename.endswith(".pdf"):
#                 pdf_path = os.path.join(cv_folder, filename)
                
#                 try:
#                     print(f"Processing {filename}...")
#                     documents = extract_pdf_content(pdf_path)
                    
#                     # Generate embeddings and store documents
#                     for doc in documents:
#                         try:
#                             embedding = embeddings.embed_query(doc["text"])
                            
#                             mongo_doc = {
#                                 "text": doc["text"],
#                                 "metadata": doc["metadata"],
#                                 "embedding_array": embedding
#                             }
                            
#                             # Insert into MongoDB
#                             collection.insert_one(mongo_doc)
#                             total_pages += 1
                            
#                         except Exception as e:
#                             print(f"Error processing page in {filename}: {str(e)}")
#                             continue
                    
#                     successful_files.append(filename)
                    
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
    processed_count = 0
    
    try:
        # Clear existing collection
        collection.delete_many({})
        
        # Process each PDF in the cv folder
        for filename in os.listdir(cv_folder):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(cv_folder, filename)
                print(f"Processing {filename}...")
                
                try:
                    # Extract content from the PDF
                    result = extract_pdf_content(pdf_path)
                    
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