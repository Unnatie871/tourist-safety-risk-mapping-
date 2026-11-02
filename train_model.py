
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Step 1: Load real crime data
df = pd.read_csv("data/ncrb_crime_data_2022.csv")

print("Real crime dataset loaded.")
print("Total district records:", len(df))

# Step 2: Select historical crime statistics as input features
features = [
    "totrape22",
    "totrape23",
    "crlhus22",
    "crlhus23",
    "dwydeath22",
    "dwydeath23",
    "acidatt22",
    "acidatt23",
    "totkidabd22",
    "totkidabd23"
]

# Step 3: Select the 2024 reported-crime total as the target
target = "totcrwom24"

# Check that the required columns exist
required_columns = features + [target]

missing = [
    column for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError("Missing columns: " + str(missing))

# Step 4: Clean and validate the selected data
data = df[required_columns].copy()

for column in required_columns:
    data[column] = pd.to_numeric(
        data[column], errors="coerce"
    )

data = data.dropna()

# Remove impossible negative counts
data = data[(data >= 0).all(axis=1)]

print("Records available after cleaning:", len(data))

if len(data) < 30:
    raise ValueError("Not enough records to train the model.")

# Step 5: Create relative reported-crime-burden categories
# These categories are based on the distribution of 2024 totals.
data["crime_category"] = pd.qcut(
    data[target].rank(method="first"),
    q=3,
    labels=["Low", "Medium", "High"]
)

X = data[features]
y = data["crime_category"]

# Step 6: Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Step 7: Train the Random Forest classifier
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# Step 8: Evaluate the model on unseen test records
predictions = model.predict(X_test)

print("\n===== MODEL EVALUATION =====")
print("Test accuracy:", round(
    accuracy_score(y_test, predictions), 3
))

print("\nClassification report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

# Step 9: Save the trained model and its feature names
joblib.dump(
    {
        "model": model,
        "features": features,
        "target": target,
        "categories": ["Low", "Medium", "High"]
    },
    "crime_model.pkl"
)

print("\nModel saved as crime_model.pkl")
print("Training completed successfully.") 