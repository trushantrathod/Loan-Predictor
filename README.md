# Loan Prediction 

A web application that predicts **loan eligibility** using a machine learning model and provides **AI-powered financial advice**.  

---

## 🚀 Features  
- **Loan Eligibility Prediction**: Predicts whether a loan application will be approved or rejected based on user input.  
- **AI-Powered Financial Advice**: Offers personalized financial suggestions depending on the prediction outcome.  
- **User-Friendly Interface**: Simple and intuitive React frontend.  
- **CORS Enabled**: Backend API is configured with CORS for frontend requests.  

---

## 🛠️ Technologies Used  

### Frontend  
- React  
- Axios  
- Testing Library  
- Web Vitals  

### Backend  
- FastAPI  
- Uvicorn  
- scikit-learn  
- Joblib  
- Pandas  
- NumPy  
- Google Generative AI  

### Machine Learning  
- **Random Forest Classifier** (for loan prediction)  
- Scikit-learn  
- Pandas  

---

## 🤖 Machine Learning Model  
The loan eligibility prediction is powered by a **Random Forest Classifier** trained on a dataset of past loan applications.  

- **Random Forest** is an ensemble method that creates multiple decision trees and outputs the majority class from them.  
- The model identifies patterns from applicant data (e.g., income, loan amount, credit history) to predict loan approval.  

---

## ⚙️ Setup and Installation  

### Prerequisites  
- Python 3.x  
- Node.js & npm  

---

### 🔹 Backend Setup  

```bash
# Clone the repository
git clone https://github.com/trushantrathod/loan-predictor.git
cd loan-predictor/backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app:app --reload
```

---

### 🔹 Frontend Setup  

```bash
cd ../frontend

# Install dependencies
npm install

# Run React server
npm start
```

---

## ▶️ Usage  
1. Open browser and go to **http://localhost:3000**.  
2. Fill in the loan application form with details.  
3. Click **Predict Eligibility** to see loan prediction and financial advice.  

---

## 📂 Project Structure  

```
loan-predictor/
├── backend/
│   ├── app.py
│   ├── model.joblib
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src/
│   │   ├── App.css
│   │   ├── App.js
│   │   ├── index.css
│   │   ├── index.js
│   │   ├── reportWebVitals.js
│   │   └── setupTests.js
│   ├── package.json
│   └── package-lock.json
└── ml/
    ├── data/
    │   ├── test.csv
    │   └── train.csv
    └── train.py
```

---

## 📌 Future Enhancements  
- Add more ML models and compare accuracy.  
- Integrate advanced financial advice with AI.  
- Deploy backend & frontend on cloud platforms (AWS, GCP, or Heroku).  
- Implement authentication & user loan history tracking.  

---
