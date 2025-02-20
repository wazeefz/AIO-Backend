import os
from io import BytesIO
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field
from pypdf import PdfReader

app = FastAPI()
load_dotenv()
llm = GoogleGenerativeAI(
    model='gemini-1.5-flash',
    temperature=0,
    api_key=os.getenv('GEMINI_API_KEY')
)

# Add CORS middleware with specific origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_pdf_file(file_contents:BytesIO):
    try:
        pdf_reader = PdfReader(file_contents)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

class ResumeReport(BaseModel):
    name: str = Field(description="Name of the employee")
    address: str = Field(description="address of the employee")
    contact_details: str = Field(description="contact details of the employee")
    skills: List[str] = Field(description="List of skills")
    education: List[str] = Field(description="education details of the employee")
    profesional_summary: str = Field(description="professional summary of the employee")

@app.post("/summarize_resume")
async def summarize_resume(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        contents = await file.read()
        file_contents = BytesIO(contents)
        text = read_pdf_file(file_contents)

        prompt = """
        You are a meticulous hiring manager tasked with extracting key information from a resume. Your job is to convert the unstructured data into structured JSON format.

        Please extract the information from the resume provided below, delimited by triple backticks, and present it as a JSON object with the following fields. If any information is missing, include the key with a `null` value:

        Fields to extract:

        1. name: Full name of the candidate.

        2. address: The address provided by the candidate (if available).

        3. contact_details: Includes: phone: Phone number. Example: `+60123456789`
            - email: Email address. Example: `work@yahoo.com`
            - socials: A dictionary of the candidates social media profiles, such as LinkedIn and GitHub. 

        4. skills: List of technical, professional, and language skills. Include co-curricular activity skills (if explicitly mentioned as skills). Do not include hobbies or interests unless they are marked as skills.

        5. education: List of educational qualifications with the following details:
            - institution: Name of the institution.
            - level: Level of education (e.g., Bachelor's, Master's, PhD).
            - degree: Specific degree title (e.g., Bachelor of Information Systems (Honours) (Data Analytics)).
            - field: Extract the field from the degree. Example: "Information Systems" for "Bachelor of Information Systems".
            - cgpa: Cumulative Grade Point Average, if provided.
            - start_year: Start year of the program.
            - graduation_year: Graduation or expected graduation year.

        6. professional_summary: Write a concise and well-crafted summary of the candidate's experience, skills, and qualifications based on the extracted information.

        ```{text}```
        
        Please ensure the JSON output is correctly formatted, ignore newline chracters (such as '\n'), follows the field requirements strictly, and provides accurate interpretations of the data.
        """

        prompt_template = PromptTemplate(template=prompt, input_variables=["text"])
        output_parser = JsonOutputParser(pydantic_object=ResumeReport)
        
        # Create the chain correctly
        chain = (
            prompt_template 
            | llm 
            | output_parser
        )
        
        # Invoke chain with the text
        response = chain.invoke({"text": text})
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")