import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // Import the stylesheet

const formFields = {
    personal: [
        { name: "Gender", label: "Gender", type: "select", options: ["Male", "Female"] },
        { name: "Married", label: "Married", type: "select", options: ["No", "Yes"] },
        { name: "Dependents", label: "Dependents", type: "select", options: ["0", "1", "2", "3+"] },
        { name: "Education", label: "Education", type: "select", options: ["Graduate", "Not Graduate"] },
        { name: "Self_Employed", label: "Self Employed", type: "select", options: ["No", "Yes"] },
    ],
    financial: [
        { name: "ApplicantIncome", label: "Applicant Income", type: "number", placeholder: "e.g. 50000", adornment: { position: 'prefix', content: '₹' } },
        { name: "CoapplicantIncome", label: "Co-applicant Income", type: "number", placeholder: "e.g. 25000", adornment: { position: 'prefix', content: '₹' } },
        { name: "LoanAmount", label: "Loan Amount(thousands)", type: "number", placeholder: "e.g. 150" },
        { name: "Loan_Amount_Term", label: "Loan Term (months)", type: "number", placeholder: "e.g. 360" },
    ],
    property: [
        { name: "Credit_History", label: "Credit History", type: "select", options: [{ label: "Available", value: "1" }, { label: "Not Available", value: "0" }] },
        { name: "Property_Area", label: "Property Area", type: "select", options: ["Urban", "Semiurban", "Rural"] },
        { name: "Loan_Type", label: "Loan Purpose", type: "select", options: ["House", "Car", "Education", "Personal", "Business"] },
    ]
};

// --- Initial State for the Form ---
const initialState = {
    Gender: "Male", Married: "No", Dependents: "0", Education: "Graduate", Self_Employed: "No",
    ApplicantIncome: "", CoapplicantIncome: "", LoanAmount: "", Loan_Amount_Term: "360",
    Credit_History: "1", Property_Area: "Urban", CIBIL_Score: "650", Loan_Type: "House",
};

// --- Reusable Input Component ---
const FormInput = ({ field, value, onChange }) => {
    const commonProps = { name: field.name, id: field.name, value, onChange, required: true };

    if (field.type === "select") {
        return (
            <select {...commonProps}>
                {field.options.map((opt) => (
                    <option key={opt.value || opt} value={opt.value || opt}>{opt.label || opt}</option>
                ))}
            </select>
        );
    }

    if (field.adornment) {
        return (
            <div className="input-wrapper">
                <span className={`input-adornment ${field.adornment.position}`}>{field.adornment.content}</span>
                <input type={field.type} placeholder={field.placeholder} {...commonProps} />
            </div>
        );
    }

    return <input type={field.type} placeholder={field.placeholder} {...commonProps} />;
};

// --- CIBIL Score Slider Component ---
const CibilSlider = ({ value, onChange }) => {
    const [showInfo, setShowInfo] = useState(false);

    const getCibilColor = (score) => {
        if (score < 550) return 'red';
        if (score < 750) return 'yellow';
        return 'green';
    };

    const progress = ((value - 300) / 600) * 100;

    const handleInputBlur = (e) => {
        let numericValue = parseInt(e.target.value, 10);
        if (isNaN(numericValue) || numericValue < 300) {
            numericValue = 300;
        }
        if (numericValue > 900) {
            numericValue = 900;
        }
        onChange({ target: { name: 'CIBIL_Score', value: numericValue.toString() } });
    };

    return (
        <div className="cibil-slider-container">
            <div className="cibil-label-input-wrapper">
                <div className="label-with-info">
                    <label htmlFor="CIBIL_Score">CIBIL Score</label>
                    <button type="button" className="info-button" onClick={() => setShowInfo(!showInfo)}>
                        i
                    </button>
                    {showInfo && (
                        <div className="cibil-info-tooltip">
                            <h4>CIBIL Score Ranges</h4>
                            <ul>
                                <li><strong>300-549:</strong> Poor</li>
                                <li><strong>550-649:</strong> Average</li>
                                <li><strong>650-749:</strong> Good</li>
                                <li><strong>750-900:</strong> Excellent</li>
                            </ul>
                        </div>
                    )}
                </div>
                <input
                    type="number"
                    name="CIBIL_Score"
                    id="CIBIL_Score"
                    className="cibil-number-input"
                    value={value}
                    onChange={onChange}
                    onBlur={handleInputBlur}
                    min="300"
                    max="900"
                    placeholder="300-900"
                />
            </div>
            <div className="slider-wrapper">
                <div className="cibil-slider-track">
                    <div className={`cibil-slider-progress ${getCibilColor(value)}`} style={{ width: `${progress}%` }}></div>
                </div>
                <input
                    type="range"
                    name="CIBIL_Score"
                    className="cibil-slider"
                    min="300"
                    max="900"
                    value={value}
                    onChange={onChange}
                />
            </div>
        </div>
    );
};


// --- Result Card Component ---
const ResultCard = ({ result }) => {
    const isApproved = result.eligible;
    const statusClass = isApproved ? "approved" : "rejected";
    const Icon = isApproved ? CheckCircleIcon : XCircleIcon;

    return (
        <div className={`result-card ${statusClass}`}>
            <div className="result-header">
                <Icon className="result-icon" />
                <div className="result-header-text">
                    <h2>Loan {isApproved ? "Approved" : "Rejected"}</h2>
                    <p>Model Confidence: <strong>{(result.probability * 100).toFixed(1)}%</strong></p>
                </div>
            </div>
            <div className="result-body">
                <h3>Personalized Financial Plan</h3>
                <div className="analysis-content">
                    {result.analysis.split('\n').filter(p => p.trim() !== '').map((paragraph, index) => (
                        <p key={index}>{paragraph}</p>
                    ))}
                </div>
            </div>
        </div>
    );
};

// --- Main App Component ---
export default function App() {
    const [formData, setFormData] = useState(initialState);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setResult(null);

        // Prepare data with correct numeric types
        const dataToSend = {
            ...formData,
            ApplicantIncome: Number(formData.ApplicantIncome) || 0,
            CoapplicantIncome: Number(formData.CoapplicantIncome) || 0,
            LoanAmount: Number(formData.LoanAmount) || 0,
            Loan_Amount_Term: Number(formData.Loan_Amount_Term),
            Credit_History: Number(formData.Credit_History),
            CIBIL_Score: Number(formData.CIBIL_Score),
        };

        try {
            const res = await axios.post("http://127.0.0.1:8000/predict", dataToSend);
            setResult(res.data);
        } catch (err) {
            setError("Failed to connect to the prediction service. Please ensure the backend is running and reachable.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-container">
            <main className="main-content">
                <header className="app-header">
                    <h1 className="header-title">Loan Prediction</h1>
                    <p className="header-subtitle">Enter your details for an instant eligibility check and a personalized financial plan.</p>
                </header>

                <form className="loan-form" onSubmit={handleSubmit} noValidate>
                    <fieldset className="form-fieldset">
                        <legend>Personal Details</legend>
                        <div className="fieldset-grid three-columns">
                            {formFields.personal.map(field => (
                                <div className="form-group" key={field.name}>
                                    <label htmlFor={field.name}>{field.label}</label>
                                    <FormInput field={field} value={formData[field.name]} onChange={handleChange} />
                                </div>
                            ))}
                        </div>
                    </fieldset>

                    <fieldset className="form-fieldset">
                        <legend>Financial Details</legend>
                        <div className="fieldset-grid two-columns">
                            {formFields.financial.map(field => (
                                <div className="form-group" key={field.name}>
                                    <label htmlFor={field.name}>{field.label}</label>
                                    <FormInput field={field} value={formData[field.name]} onChange={handleChange} />
                                </div>
                            ))}
                        </div>
                        <CibilSlider value={formData.CIBIL_Score} onChange={handleChange} />
                    </fieldset>

                    <fieldset className="form-fieldset">
                        <legend>Loan & Property Details</legend>
                        <div className="fieldset-grid three-columns">
                            {formFields.property.map(field => (
                                <div className="form-group" key={field.name}>
                                    <label htmlFor={field.name}>{field.label}</label>
                                    <FormInput field={field} value={formData[field.name]} onChange={handleChange} />
                                </div>
                            ))}
                        </div>
                    </fieldset>

                    <button type="submit" className="submit-button" disabled={loading}>
                        {loading ? (
                            <>
                                <SpinnerIcon className="loading-spinner" />
                                Analyzing...
                            </>
                        ) : "Predict Eligibility"}
                    </button>
                </form>

                {error && <div className="error-message">{error}</div>}
                {result && <ResultCard result={result} />}
            </main>
        </div>
    );
}

// --- SVG Icons ---
const CheckCircleIcon = (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const XCircleIcon = (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const SpinnerIcon = (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" {...props}>
        <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 3a9 9 0 100 18 9 9 0 000-18z" opacity=".25"></path>
        <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 12a9 9 0 01-9 9"></path>
    </svg>
);

