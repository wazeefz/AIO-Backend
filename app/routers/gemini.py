import os
from io import BytesIO
from typing import List, Optional, Union

from dotenv import load_dotenv
from fastapi import APIRouter, File, HTTPException, UploadFile
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field
from pypdf import PdfReader

load_dotenv()

router = APIRouter(prefix="/gemini", tags=["Gemini AI"])

llm = GoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    api_key=os.getenv("GEMINI_API_KEY"),
)


def read_pdf_file(file_contents: BytesIO):
    """Extract text from a PDF file."""
    try:
        pdf_reader = PdfReader(file_contents)
        text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")


class ResumeReport(BaseModel):
    name: Optional[str] = Field(None, description="Name of the employee")
    address: Optional[str] = Field(None, description="Address of the employee")
    contact_details: Optional[Union[dict, str]] = Field(
        None, description="Contact details including phone, email, and social links"
    )
    skills: Optional[List[str]] = Field(None, description="List of skills")
    education: Optional[Union[List[dict], str]] = Field(
        None, description="Education details"
    )
    professional_summary: Optional[str] = Field(None, description="Professional summary")


@router.post("/summarize_resume")
async def summarize_resume(file: UploadFile = File(...)):
    """Extract structured data from a resume (PDF) using Gemini API."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        contents = await file.read()
        text = read_pdf_file(BytesIO(contents))

        prompt = f"""
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
        output_parser = JsonOutputParser()

        # Execute the chain
        chain = prompt_template | llm | output_parser
        response = chain.invoke({"text": text})

        if not isinstance(response, dict):
            raise ValueError("Invalid response format from Gemini")

        return response  # Directly return as a dictionary

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
