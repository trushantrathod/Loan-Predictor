from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os # ✅ NEW: To handle environment variables for security
import time

# ✅ NEW: Import and configure the Gemini API
import google.generativeai as genai

# --- IMPORTANT: Configure your Gemini API Key ---
# Replace "YOUR_GEMINI_API_KEY" with the key you just copied.
# For better security, it's recommended to use an environment variable:
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key="") 


app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ UPGRADED: Gemini function with a much more powerful prompt
# Inside the get_gemini_analysis function in app.py
# In app.py, replace the whole function with this final version:

def get_gemini_analysis(applicant_data: dict, prediction_result: dict):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        status = "Approved" if prediction_result["eligible"] else "Rejected"
        credit_history_status = "Good" if applicant_data['Credit_History'] == 1.0 else "Bad or Not Available"
        total_income = applicant_data['ApplicantIncome'] + applicant_data['CoapplicantIncome']
        
        # ✅ UPDATED PROMPT: Removed the instruction to use bold formatting.
        prompt = f"""
        You are an expert financial advisor creating a detailed action plan for a loan applicant.
        The application status is: **{status}**.

        Applicant's Financial Profile:
        - Total Monthly Income: ₹{total_income}
        - Loan Amount: ₹{applicant_data['LoanAmount'] * 1000}
        - Credit History: {credit_history_status}

        Your Task:
        1.  Start with a brief, empathetic introductory sentence.
        2.  Provide a numbered list of **exactly 5 actionable recommendations**.
        3.  For each recommendation, first state the goal (e.g., "Improve Your Credit Score"), and then briefly explain how the user can achieve this.
        4.  Base your advice on the applicant's specific financial profile.
        5.  **IMPORTANT SAFETY RULE: If the loan was Rejected, under no circumstances should you advise the applicant to ask for a larger loan amount. All advice for a rejected loan must focus on improving financial health, increasing savings, reducing debt, or reducing the requested loan amount.**
        6.  Address the applicant directly using "you" and "your".
        """
        
        response = model.generate_content(prompt)
        # ✅ NEW: Clean the response to ensure no markdown is left.
        clean_response = response.text.replace('**', '')
        return clean_response

    except Exception as e:
        print(f"Error calling Gemini API: {e}") 
        return "We couldn't generate personalized tips at this moment. For a rejected application, key areas to focus on are improving your credit score and ensuring your income comfortably covers the loan amount. For an approved loan, always prioritize timely payments."

@app.get("/")
def home():
    return {"message": "Loan Prediction API is running 🚀"}

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

model = joblib.load("model.joblib")

@app.post("/predict")
def predict(applicant: Applicant):
    applicant_dict = applicant.dict()
    
    data = pd.DataFrame([applicant_dict])
    pred = model.predict(data)[0]
    prob = model.predict_proba(data)[0][1]
    
    result = {
        "eligible": bool(pred),
        "probability": round(float(prob), 3),
    }
    
    analysis_tips = get_gemini_analysis(applicant_dict, result)
    
    final_response = {
        **result,
        "analysis": analysis_tips,
        "currency": "₹"
    }
    
    return final_response
