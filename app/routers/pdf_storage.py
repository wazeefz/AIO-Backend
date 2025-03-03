from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import os

router = APIRouter(prefix="/upload-pdf", tags=["PDF Storage"])

# Path to your Google Drive API credentials JSON file
SERVICE_ACCOUNT_FILE = 'service_account.json'

# Scopes required for accessing Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# ID of the parent folder in Google Drive where the file will be uploaded
PARENT_FOLDER_ID = "1kBeyHjaKLYQLamyzksjufmT4ox-7Ct4l"

def authenticate():
    """Authenticate using the service account credentials."""
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    """Endpoint to upload a PDF file to Google Drive directly."""
    try:
        # Authenticate with Google Drive
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        # Define file metadata, including the parent folder ID
        file_metadata = {
            'name': file.filename,
            'parents': [PARENT_FOLDER_ID]
        }

        # Read the file content into memory
        file_content = await file.read()

        # Use MediaIoBaseUpload to handle the file upload directly from memory
        media = MediaIoBaseUpload(BytesIO(file_content), mimetype='application/pdf', resumable=True)

        # Upload the file to Google Drive
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return {"file_id": uploaded_file.get('id')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.get("/")
async def get_file(file_id: str = Query(..., description="The Google Drive file ID")):
    """Endpoint to retrieve file metadata from Google Drive."""
    try:
        # Authenticate with Google Drive
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        # Get file metadata
        file_metadata = service.files().get(fileId=file_id, fields="id, name, mimeType, createdTime").execute()

        return file_metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve file: {str(e)}")

@router.put("/")
async def update_file(file_id: str = Query(..., description="The Google Drive file ID"), file: UploadFile = File(...)):
    """Endpoint to update a file in Google Drive."""
    try:
        # Authenticate with Google Drive
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        # Read the new file content into memory
        file_content = await file.read()

        # Use MediaIoBaseUpload to handle the file upload directly from memory
        media = MediaIoBaseUpload(BytesIO(file_content), mimetype='application/pdf', resumable=True)

        # Update the file in Google Drive
        updated_file = service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id'
        ).execute()

        return {"file_id": updated_file.get('id')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")

@router.delete("/")
async def delete_file(file_id: str = Query(..., description="The Google Drive file ID")):
    """Endpoint to delete a file from Google Drive."""
    try:
        # Authenticate with Google Drive
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        # Delete the file
        service.files().delete(fileId=file_id).execute()

        return {"message": f"File with ID {file_id} has been deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")