import React, { useState } from "react";
import axios from "axios";
import "./App.css";

// --- Configuration array for form fields ---
const formFields = [
  { name: "Gender", label: "Gender", type: "select", options: ["Male", "Female"] },
  { name: "Married", label: "Married", type: "select", options: ["No", "Yes"] },
  { name: "Dependents", label: "Dependents", type: "select", options: ["0", "1", "2", "3+"] },
  { name: "Education", label: "Education", type: "select", options: ["Graduate", "Not Graduate"] },
  { name: "Self_Employed", label: "Self Employed", type: "select", options: ["No", "Yes"] },
  { name: "ApplicantIncome", label: "Applicant Income", type: "number", placeholder: "e.g., 50000" },
  { name: "CoapplicantIncome", label: "Coapplicant Income", type: "number", placeholder: "e.g., 25000" },
  { name: "LoanAmount", label: "Loan Amount (in thousands)", type: "number", placeholder: "e.g., 150" },
  { name: "Loan_Amount_Term", label: "Loan Term (Months)", type: "number", placeholder: "e.g., 360" },
  { name: "Credit_History", label: "Credit History", type: "select", options: [{label: "1 (Good)", value: "1"}, {label: "0 (Bad)", value: "0"}] },
  { name: "Property_Area", label: "Property Area", type: "select", options: ["Urban", "Semiurban", "Rural"] },
];

export default function App() {
  // --- STATE MANAGEMENT ---
  const [formData, setFormData] = useState({
    Gender: "Male",
    Married: "No",
    Dependents: "0",
    Education: "Graduate",
    Self_Employed: "No",
    ApplicantIncome: "",
    CoapplicantIncome: "",
    LoanAmount: "",
    Loan_Amount_Term: "360",
    Credit_History: "1",
    Property_Area: "Urban",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resultKey, setResultKey] = useState(0);

  // --- HANDLERS ---
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    for (const field of formFields) {
      if (formData[field.name] === "") {
        setError(`Please fill in the "${field.label}" field.`);
        setLoading(false);
        setResultKey(prevKey => prevKey + 1);
        return;
      }
    }

    const dataToSend = {
      ...formData,
      ApplicantIncome: Number(formData.ApplicantIncome),
      CoapplicantIncome: Number(formData.CoapplicantIncome),
      LoanAmount: Number(formData.LoanAmount),
      Loan_Amount_Term: Number(formData.Loan_Amount_Term),
      Credit_History: Number(formData.Credit_History),
    };

    try {
      const res = await axios.post("http://127.0.0.1:8000/predict", dataToSend);
      setResult(res.data);
    } catch (err) {
      console.error("API Error:", err);
      setError("Failed to connect to the prediction service. Please try again later.");
    } finally {
      setLoading(false);
      setResultKey(prevKey => prevKey + 1);
    }
  };

  // --- DYNAMIC FIELD RENDERER ---
  const renderField = (field) => {
    if (field.type === "select") {
      return (
        <div className="select-wrapper">
          <select name={field.name} id={field.name} value={formData[field.name]} onChange={handleChange} required>
            {field.options.map((option) => (<option key={option.value || option} value={option.value || option}>{option.label || option}</option>))}
          </select>
        </div>
      );
    }
    return (<input type={field.type} name={field.name} id={field.name} placeholder={field.placeholder || ""} value={formData[field.name]} onChange={handleChange} required />);
  };

  // --- RENDER ---
  return (
    <div className="container">
      <h1>Loan Eligibility Predictor</h1>
      <form onSubmit={handleSubmit} noValidate>
        {formFields.map((field) => (<div className="form-group" key={field.name}><label htmlFor={field.name}>{field.label}</label>{renderField(field)}</div>))}
        <button type="submit" disabled={loading}>{loading ? "Predicting..." : "Predict Eligibility"}</button>
      </form>

      {/* --- UNIFIED RESULT AND ERROR DISPLAY --- */}
      <div
        key={resultKey}
        // ✅ NEW: Add an 'analysing' class when loading is true
        className={`result ${
          loading ? "analysing" : ""
        } ${
          result ? (result.eligible ? "approved" : "rejected") : ""
        } ${error ? "rejected" : ""}`}
      >
        {/* ✅ NEW: Show a special message during the loading delay */}
        {loading && <p className="analysing-text">AI is analysing your profile...</p>}
        
        {/* These only show when loading is false */}
        {!loading && error && <p>{error}</p>}
        {!loading && result && (
          <>
            <p className="status-message">{result.eligible ? "🎉 Loan Approved! 🎉" : "Loan Application Rejected"}</p>
            <div className="gemini-analysis">{result.analysis}</div>
            <p className="confidence-score"><b>Model Confidence:</b> {(result.probability * 100).toFixed(1)}%</p>
          </>
        )}
      </div>
    </div>
  );
}