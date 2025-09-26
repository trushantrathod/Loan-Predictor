import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. Load the new dataset with CIBIL scores
train_df = pd.read_csv("data/train_with_cibil.csv")

# Drop Loan_ID as it's not a predictive feature
train_df = train_df.drop("Loan_ID", axis=1)


# 2. Preprocess Target Variable
train_df["Loan_Status"] = train_df["Loan_Status"].map({"Y": 1, "N": 0})
# Drop rows where Loan_Status is missing (if any)
train_df.dropna(subset=['Loan_Status'], inplace=True)
train_df["Loan_Status"] = train_df["Loan_Status"].astype(int)


loan_types = ['Personal', 'House', 'Car', 'Education']
train_df['Loan_Type'] = np.random.choice(loan_types, size=len(train_df))


cat_cols = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area", "Loan_Type"]
num_cols = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History", "CIBIL_Score"]

# Define features (X) and target (y)
X = train_df[cat_cols + num_cols]
y = train_df["Loan_Status"]


# 5. Define Preprocessing Pipelines (no changes needed here)
num_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

cat_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])


# 6. Create the ColumnTransformer (no changes needed here)
preprocessor = ColumnTransformer([
    ("num", num_pipe, num_cols),
    ("cat", cat_pipe, cat_cols)
])


# 7. Create the Final Classifier Pipeline
clf = Pipeline([
    ("prep", preprocessor),
    ("rf", RandomForestClassifier(n_estimators=200, random_state=42))
])


# 8. Split Data and Train the Model
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
clf.fit(X_train, y_train)


# 9. Evaluate the Model
y_pred = clf.predict(X_valid)
print("Validation accuracy:", accuracy_score(y_valid, y_pred))
print("\nClassification Report:\n", classification_report(y_valid, y_pred))


# 10. Save the Model
joblib.dump(clf, "../backend/model.joblib")
print("✅ Model saved to backend/model.joblib")
