import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 1. Generate synthetic dataset for Customer Churn
np.random.seed(42)
n_samples = 1000

data = {
    'credit_score': np.random.randint(300, 850, n_samples),
    'age': np.random.randint(18, 70, n_samples),
    'tenure': np.random.randint(0, 10, n_samples),
    'balance': np.random.uniform(0, 100000, n_samples),
    'num_products': np.random.randint(1, 5, n_samples),
}

df = pd.DataFrame(data)

# High churn target rule (older age + lower credit score + higher balance = higher risk)
df['churn'] = (
    (df['age'] > 40) & (df['credit_score'] < 600) | (df['balance'] > 60000)
).astype(int)

X = df.drop('churn', axis=1)
y = df['churn']

# 2. Train-Test Split & Fit Model
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 3. Save Trained Model to File
joblib.dump(model, 'churn_model.joblib')
print(
    "✅ Model trained and saved successfully as 'churn_model.joblib'!"
)