from . import database, schemas 
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db

router = APIRouter()

# PDF Upload Endpoint
@router.post("/upload-pdf/")
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
@router.get("/list-pdfs/")
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
