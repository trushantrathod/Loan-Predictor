import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

train_df = pd.read_csv("data/train.csv")
test_df = pd.read_csv("data/test.csv")

train_df["Loan_Status"] = train_df["Loan_Status"].map({"Y": 1, "N": 0})

cat_cols = ["Gender","Married","Dependents","Education","Self_Employed","Property_Area"]
num_cols = ["ApplicantIncome","CoapplicantIncome","LoanAmount","Loan_Amount_Term","Credit_History"]

X = train_df[cat_cols + num_cols]
y = train_df["Loan_Status"]

num_pipe = Pipeline([("imputer",SimpleImputer(strategy="median")),("scaler",StandardScaler())])
cat_pipe = Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("ohe",OneHotEncoder(handle_unknown="ignore"))])

preprocessor = ColumnTransformer([("num",num_pipe,num_cols),("cat",cat_pipe,cat_cols)])

clf = Pipeline([("prep",preprocessor),("rf",RandomForestClassifier(n_estimators=200,random_state=42))])

X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_valid)
print("Validation accuracy:", accuracy_score(y_valid, y_pred))
print(classification_report(y_valid, y_pred))

joblib.dump(clf, "../backend/model.joblib")
print("✅ Model saved to backend/model.joblib")
