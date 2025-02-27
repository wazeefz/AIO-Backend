from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from . import models
from .routers import department, skill, talent, project, user, gemini, rag, pdf_loader, pdf_loader_omar, chat, projectassignments, talentskill

# Initialize DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(department.router)
app.include_router(skill.router)
app.include_router(talent.router)
app.include_router(project.router)
app.include_router(user.router)
app.include_router(gemini.router)
app.include_router(rag.router)
app.include_router(pdf_loader.router)
app.include_router(pdf_loader_omar.router)
app.include_router(chat.router)
app.include_router(projectassignments.router)
app.include_router(talentskill.router)

@app.get("/")
def home():
    return {"message": "Welcome to AIO Backend! Please proceed to http://127.0.0.1:8000/docs to test the app."}
