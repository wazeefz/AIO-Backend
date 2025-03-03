from fastapi import APIRouter, File, UploadFile, HTTPException

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import os
import io
import logging
import requests

router = APIRouter(prefix="/upload-pdf", tags=["PDF Storage"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FOLDER_ID = '1bXUM5xHY5jJ4aGC6n9YjnC9uhPdzPBuE'

# Endpoint to handle file upload
@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Validate file type
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are allowed.")

        # Read the file content
        file_content = await file.read()

        # Upload the file to Google Drive
        upload_url = f"https://www.googleapis.com/upload/drive/v3/files?uploadType=media&supportsAllDrives=true&fields=id"
        headers = {
            "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # Replace with a valid access token
            "Content-Type": file.content_type,
        }
        data = {
            "name": file.filename,
            "parents": [FOLDER_ID],
        }
        response = requests.post(
            upload_url,
            headers=headers,
            data=file_content,
            json=data,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        # Return the file ID
        return {"file_id": response.json().get('id'), "file_name": file.filename}

    except Exception as e:
        logger.error(f"Error in upload_pdf: {e}")
        raise HTTPException(status_code=500, detail=str(e))
