# --- 0. Imports ---
import os
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# --- 1. Initialize FastAPI App ---
app = FastAPI(
    title="Loan Prediction API",
    description="An API to predict loan eligibility and provide AI-generated financial tips.",
    version="3.0.1"
)

# --- 2. Middleware Configuration ---
# --- 2. Middleware Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Load Trained Model ---
try:
    model = joblib.load("model.joblib")
except FileNotFoundError:
    model = None

# --- 4. Configure Gemini API (with Hardcoded Key) ---
# WARNING: This is NOT recommended for production or shared code.
try:
    # Directly paste your API key here
    api_key = "AIzaSyAIcd1VE4y-MVLPCTQyMz02Mgpty4ukwBo" 

    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        raise ValueError("Please replace 'YOUR_GEMINI_API_KEY_HERE' with your actual Gemini API key.")
    
    genai.configure(api_key=api_key)
    # Initialize the Gemini Pro model
    gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    gemini_model = None

# --- 5. Pydantic Model for Input Validation ---
class Applicant(BaseModel):
    Gender: str
    Married: str
    Dependents: str
    Education: str
    Self_Employed: str
    ApplicantIncome: float
    CoapplicantIncome: float
    LoanAmount: float
    Loan_Amount_Term: float
    Credit_History: float
    Property_Area: str
    CIBIL_Score: int
    Loan_Type: str

# --- 6. AI-Powered Tip Generation Function ---
async def generate_versatile_tips(applicant_data: dict, prediction_result: dict) -> str:
    """
    Generates personalized financial tips using the Gemini API.
    """
    if not gemini_model:
        return "AI analysis is currently unavailable. Please check API configuration."

    status = "Approved" if prediction_result["eligible"] else "Rejected"
    probability = prediction_result["probability"]

    prompt = f"""
    You are an expert financial advisor AI for a loan company. Your tone should be constructive, empathetic, and professional.

    An applicant has just received a decision on their loan application. Based on their data and the outcome, generate a personalized financial action plan for them.

    **Applicant's Profile:**
    - Loan Type Requested: {applicant_data['Loan_Type']}
    - CIBIL Score: {applicant_data['CIBIL_Score']}
    - Applicant's Monthly Income: ₹{applicant_data['ApplicantIncome']:,.0f}
    - Co-applicant's Monthly Income: ₹{applicant_data['CoapplicantIncome']:,.0f}
    - Total Monthly Income: ₹{applicant_data['ApplicantIncome'] + applicant_data['CoapplicantIncome']:,.0f}
    - Requested Loan Amount: ₹{applicant_data['LoanAmount']:,.0f}
    - Employment: {'Self-Employed' if applicant_data['Self_Employed'] == 'Yes' else 'Salaried'}

    **Loan Decision Details:**
    - Outcome: **{status}**
    - Confidence of Decision: {probability:.1%}

    **Your Task:**
    Write a concise analysis and provide 3-4 highly relevant, actionable tips.

    **Instructions:**
    1.  Start with a single introductory sentence that acknowledges the loan decision ({status}).
    2.  If the CIBIL score is below 750, make improving it a primary tip.
    3.  For a 'Rejected' status, focus on concrete steps to improve their financial profile for a future application.
    4.  For an 'Approved' status, focus on responsible debt management and long-term financial health.
    5.  Format each tip to start with "GOAL:".
    6.  Ensure the advice is practical and directly relates to the applicant's data provided. Do not use markdown formatting.
    """
    try:
        response = await gemini_model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        return "Could not generate AI analysis at this time. Please try again later."

# --- 7. API Endpoints ---
@app.get("/")
def home():
    """API health check endpoint."""
    return {"message": "Loan Prediction API with Gemini is operational."}

@app.post("/predict")
async def predict(applicant: Applicant):
    """Predicts loan eligibility and provides AI-generated financial analysis."""
    if model is None:
        raise HTTPException(status_code=503, detail="Machine learning model not loaded.")
    if gemini_model is None:
         raise HTTPException(status_code=503, detail="Gemini AI model not configured. Check API key.")

    applicant_dict = applicant.dict()
    data = pd.DataFrame([applicant_dict])

    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0][1]

    result = {
        "eligible": bool(prediction),
        "probability": round(float(probability), 3),
        "eligible": bool(prediction),
        "probability": round(float(probability), 3),
    }

    analysis_tips = await generate_versatile_tips(applicant_dict, result)

    final_response = {
        **result,
        "analysis": analysis_tips,
    }

    return final_response