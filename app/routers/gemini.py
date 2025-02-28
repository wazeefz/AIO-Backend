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


# @router.post("/summarize_resume")
# async def summarize_resume(file: UploadFile = File(...)):
#     """Extract structured data from a resume (PDF) using Gemini API."""
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are supported")

#     try:
#         contents = await file.read()
#         text = read_pdf_file(BytesIO(contents))

#         prompt = f"""
#         You are a meticulous hiring manager tasked with extracting key information from a resume. Your job is to convert the unstructured data into structured JSON format.

#         Please extract the information from the resume provided below, delimited by triple backticks, and present it as a JSON object with the following fields. If any information is missing, include the key with a `null` value:

#         Fields to extract:

#         1. firstName: The first name of the candidate. If you encounter a 'bin' or 'binti' keyword, then everything before that is the firstName .

#         1. lastName: The last name of the candidate. If you encounter a 'bin' or 'binti' keyword, then everything after that is the lastName .

#         2. address: The address provided by the candidate (if available).

#         3. contact_details: Includes: phone: Phone number. Example: `+60123456789`
#             - email: Email address. Example: `work@yahoo.com`
#             - socials: A dictionary of the candidates social media profiles, such as LinkedIn and GitHub. 

#         4. skills: List of technical, professional, and language skills. Include co-curricular activity skills (if explicitly mentioned as skills). Do not include hobbies or interests unless they are marked as skills.

#         5. education: List of educational qualifications with the following details:
#             - institution: Name of the institution.
#             - level: Level of education (e.g., Bachelor's, Master's, PhD).
#             - degree: Specific degree title (e.g., Bachelor of Information Systems (Honours) (Data Analytics)).
#             - field: Extract the field from the degree. Example: "Information Systems" for "Bachelor of Information Systems".
#             - cgpa: Cumulative Grade Point Average, if provided.
#             - start_year: Start year of the program.
#             - graduation_year: Graduation or expected graduation year.

#         6. professional_summary: Write a concise and well-crafted summary of the candidate's experience, skills, and qualifications based on the extracted information.

#         ```{text}```
        
#         Please ensure the JSON output is correctly formatted, ignore newline chracters (such as '\n'), follows the field requirements strictly, and provides accurate interpretations of the data.
#         """

#         prompt_template = PromptTemplate(template=prompt, input_variables=["text"])
#         output_parser = JsonOutputParser()

#         # Execute the chain
#         chain = prompt_template | llm | output_parser
#         response = chain.invoke({"text": text})

#         if not isinstance(response, dict):
#             raise ValueError("Invalid response format from Gemini")

#         return response  # Directly return as a dictionary

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@router.post("/summarize_resume")
async def summarize_resume(file: UploadFile = File(...)):
    """Extract structured data from a resume (PDF) using Gemini API."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        contents = await file.read()
        text = read_pdf_file(BytesIO(contents))

        prompt = f"""
            You are a meticulous hiring manager tasked with extracting key information from a resume. Your job is to convert the unstructured data into a structured JSON format.

            Please extract the information from the resume provided below, delimited by triple backticks, and present it as a JSON object with the following fields. If any information is missing, include the key with a `null` value:

            ### **📌 Fields to Extract**
            1. **profilePic**: URL of the candidate’s profile picture (if available). If not found, return `null`.

            2. **firstName**: The first name of the candidate.
            - If you encounter a 'bin' or 'binti' keyword, extract everything **before** that as the `firstName`.

            3. **lastName**: The last name of the candidate.
            - If you encounter a 'bin' or 'binti' keyword, extract everything **after** that as the `lastName`.

            4. **email**: Candidate's email address (must be valid format).

            5. **phone**: Candidate's phone number.
            - Example: `+60123456789`
            - Ensure it is properly formatted with country code (if available).

            6. **dateOfBirth**: The candidate's birth date in `YYYY-MM-DD` format.

            7. **age**: The candidate’s age in years.
            - Calculate it based on `dateOfBirth`.

            8. **gender**: The candidate's gender (if explicitly mentioned).

            9. **maritalStatus**: The candidate's marital status (if mentioned).

            10. **currentCountry**: The country where the candidate currently resides.

            11. **currentCity**: The city where the candidate currently resides.

            12. **willingToRelocate**: `true` if the candidate explicitly states willingness to relocate, otherwise `false`.

            13. **relocationPreferences**: A list of preferred relocation locations if mentioned.

            14. **summary**: A concise summary of the candidate’s qualifications, skills, and experience.

            15. **experience**: Number of years the candidate has been working. Strictly in numeric data type
                - Please check candidate latest and earliest working year
                - Example : 2019 is earliest and present/now is the earliest
                - Please check current year
                - experience = current year - 2019
                - return data in numeric/integer type

            16. **skills**: List of technical, professional, and language skills.
                - Do not include hobbies unless explicitly mentioned as skills.

            17. **education**: A list of educational qualifications with these details:
                - **institution**: Name of the institution.
                - **level**: Level of education (e.g., Bachelor's, Master's, PhD).
                - **degree**: Full degree title.
                - **field**: Extracted field from the degree.
                - **cgpa**: Cumulative Grade Point Average (if provided).
                - **start_year**: Start year of the program.
                - **graduation_year**: Graduation or expected graduation year.

            18. **experiences**: A list of past jobs, each with:
                - **company**: Name of the employer.
                - **position**: Job title.
                - **startDate**: Start date in `YYYY-MM-DD` format.
                - **endDate**: End date in `YYYY-MM-DD` format (or `null` if still employed).
                - **responsibilities**: List of key responsibilities.

            19. **certifications**: A list of certifications with:
                - **name**: Certification title.
                - **issuedBy**: Issuing organization.
                - **year**: Year obtained.

            20. **jobTitle**: The candidate’s desired job title.

            21. **jobPosition**: The job position level (e.g., Junior, Senior).

            22. **department**: The department the candidate works in (if mentioned).

            23. **employmentType**: Type of employment (`fullTime`, `partTime`, `contract`, etc.).

            24. **contractDuration**: The length of the employment contract (if applicable).

            25. **employmentRemarks**: Any additional employment-related remarks.

            26. **salary**: Expected or current salary in numeric format.

            ---

            ### **📌 Additional Rules**
            - **Do not hallucinate data**: If a value is missing, set it as `null` rather than guessing.
            - **Ensure correct JSON formatting**.
            - **Ignore newlines (`\n`) in the text**.
            - **Validate extracted data**:
            - Emails must match a valid email format.
            - Phone numbers should contain only numbers and valid symbols (`+`, `-`, `()`, `.`).
            - Dates should be in `YYYY-MM-DD` format.
            - If `firstName`, `lastName`, `email`, or `phone` is uncertain, return `null`.

            ```{text}```

            Please ensure the JSON output is correctly formatted and follows these rules strictly.
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

