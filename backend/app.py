from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

# --- 1. Initialize FastAPI App ---
app = FastAPI(
    title="Loan Prediction API",
    description="An API to predict loan eligibility and provide versatile financial tips.",
    version="2.0.0"
)

# --- 2. Middleware Configuration ---
app.add_middleware(
    CORSMiddleware,
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

# --- 4. Pydantic Model for Input Validation ---
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

# --- 5. Versatile Tips Database ---
# This dictionary holds specific tips for different loan types and outcomes.
TIPS_DATABASE = {
    "Car Loan": {
        "Approved": [
            "GOAL: Secure The Best Insurance. Your loan is for a major asset. Compare insurance quotes from multiple providers to get comprehensive coverage at a good price before finalizing the purchase.",
            "GOAL: Plan for Maintenance Costs. Beyond the EMI, budget for annual expenses like insurance renewal, servicing, and potential repairs to avoid financial surprises."
        ],
        "Rejected": [
            "GOAL: Consider a Larger Down Payment. A smaller loan amount is less risky for lenders. Saving for a larger down payment can significantly increase your approval chances for a car loan.",
            "GOAL: Explore Pre-Owned Vehicle Options. Certified pre-owned cars often come with warranties but require a smaller loan, making them easier to get approved for."
        ]
    },
    "Home Loan": {
        "Approved": [
            "GOAL: Plan for Registration and Stamp Duty. This is a major expense not covered by the loan. Ensure you have separate funds (often 5-7% of property value) set aside for these legal formalities.",
            "GOAL: Consider Loan Prepayment. Even small, regular prepayments on your home loan can save you lakhs in interest over the long term. Check with your bank about prepayment charges."
        ],
        "Rejected": [
            "GOAL: Improve Your Debt-to-Income Ratio. Home loans are large commitments. Lenders need to see that you have minimal existing debt. Focus on closing smaller loans or credit card dues before re-applying.",
            "GOAL: Arrange for a Higher Down Payment. For home loans, a down payment of over 20% makes your application much stronger and shows financial stability."
        ]
    },
    "Personal Loan": {
        "Approved": [
            "GOAL: Stick to a Repayment Plan. Personal loans are versatile. Use the funds for the intended purpose and avoid frivolous spending to ensure you can comfortably manage the EMIs.",
            "GOAL: Avoid Taking on More Debt. While you have this loan, try to limit applying for new credit cards or other loans to keep your debt-to-income ratio healthy."
        ],
        "Rejected": [
            "GOAL: Clearly State the Purpose of the Loan. Lenders are more likely to approve a personal loan if you have a clear, justifiable reason for needing the funds, such as debt consolidation or a medical emergency.",
            "GOAL: Check for Errors in Your Credit Report. A simple error on your credit report could be impacting your score and leading to rejection. Get a free report and dispute any inaccuracies."
        ]
    },
    "Education Loan": {
        "Approved": [
            "GOAL: Focus on Your Studies. The best return on this loan is completing your education successfully to secure a good job. Make that your top priority.",
            "GOAL: Understand the Moratorium Period. You typically don't have to start paying EMIs immediately. Know when your moratorium period ends and when the first payment is due."
        ],
        "Rejected": [
            "GOAL: Include a Strong Co-Applicant. For education loans, the financial strength of your co-applicant (usually a parent) is critical. Ensure they have a stable income and a good CIBIL score.",
            "GOAL: Provide a Clear Admission Letter. The loan application must be supported by a confirmed admission letter from a recognized institution. A provisional letter may not be sufficient."
        ]
    },
    "Generic": {
        "Approved": [
            "GOAL: Automate Your EMI Payments. Set up an auto-debit instruction with your bank to ensure your EMIs are never missed, which helps maintain a strong CIBIL score.",
            "GOAL: Understand Your Loan Statement. Keep an eye on your loan account to track the principal and interest components. This helps you stay in control of your finances."
        ],
        "Rejected": [
            "GOAL: Increase Your Total Income. If possible, consider adding a co-applicant with a stable income. This increases the total household income and strengthens your application.",
            "GOAL: Seek a Smaller Loan Amount. Re-assess your needs and check if a smaller loan amount would suffice. This reduces the risk for the lender and increases approval odds."
        ]
    }
}

# --- 6. Advanced Tip Generation Function ---
def generate_versatile_tips(applicant_data: dict, prediction_result: dict) -> str:
    """
    Generates personalized financial tips using a structured database.
    """
    status_key = "Approved" if prediction_result["eligible"] else "Rejected"
    cibil_score = applicant_data['CIBIL_Score']
    loan_type = applicant_data['Loan_Type']

    analysis_points = []

    # Start with an introduction based on the loan status
    if status_key == "Approved":
        intro = "Congratulations on your loan approval! Here is a constructive action plan:"
    else:
        intro = "We understand this result may be disappointing. Here is an action plan to strengthen your financial profile:"

    # 1. Add a universal tip based on CIBIL score (always relevant)
    if cibil_score < 680:
        analysis_points.append(
            "GOAL: Improve Your CIBIL Score. A score below 680 is a primary area for improvement. Focus on paying all existing bills on time, as this has the biggest impact."
        )
    else:
        analysis_points.append(
            "GOAL: Maintain Your Strong CIBIL Score. Your score is a valuable asset. Continue your timely payments and keep credit utilization low to maintain it."
        )

    # 2. Get specific tips from the database for the given loan type
    # If the loan_type is not found, it defaults to 'Generic'
    specific_tips_category = TIPS_DATABASE.get(loan_type, TIPS_DATABASE["Generic"])
    specific_tips = specific_tips_category[status_key]
    analysis_points.extend(specific_tips)

    # 3. Add a final generic good habit tip
    analysis_points.append(
        "GOAL: Build a Strong Savings Habit. Aim to save at least 15-20% of your monthly income. A healthy emergency fund makes your financial profile much more attractive."
    )
    
    # Assemble the final response, ensuring a max of 5 tips
    final_analysis = intro + "\n\n"
    for i, point in enumerate(analysis_points[:5], 1): # Slice to ensure we don't exceed 5 points
        final_analysis += f"{i}. {point}\n"

    return final_analysis

# --- 7. API Endpoints ---
@app.get("/")
def home():
    return {"message": "Loan Prediction API is operational."}

@app.post("/predict")
def predict(applicant: Applicant):
    if model is None:
        return {"error": "Model not loaded. Please ensure 'model.joblib' is in the correct directory."}
        
    applicant_dict = applicant.dict()
    data = pd.DataFrame([applicant_dict])
    
    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0][1]
    
    result = {
        "eligible": bool(prediction),
        "probability": round(float(probability), 3),
    }
    
    analysis_tips = generate_versatile_tips(applicant_dict, result)
    
    final_response = {
        **result,
        "analysis": analysis_tips,
    }
    
    return final_response

