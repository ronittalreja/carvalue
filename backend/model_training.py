# model_training.py
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# 1️⃣ Load dataset
df = pd.read_excel("cars24.csv")
df = df.dropna()

# 2️⃣ Extract company and car_model
df["company"] = df["Car Name"].apply(lambda x: x.split()[0])
df["car_model"] = df["Car Name"].apply(lambda x: " ".join(x.split()[1:]))

# 3️⃣ Clean kms_driven
df["kms_driven"] = (
    df["Distance"].astype(str)
    .str.replace(",", "")
    .str.extract(r"(\d+)")
    .astype(float)
)

# 4️⃣ Rename columns for consistency
df.rename(columns={
    "Year": "year",
    "Fuel": "fuel_type",
    "Owner": "owners",
    "Drive": "transmission",
    "Price": "price"
}, inplace=True)

df["year"] = df["year"].astype(int)

# 5️⃣ Select features and target (only needed columns)
X = df[["company", "car_model", "year", "kms_driven", "fuel_type", "transmission", "owners"]]
y = df["price"]

# 6️⃣ One-hot encode categorical variables
X = pd.get_dummies(X, drop_first=True)

# 7️⃣ Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 8️⃣ Train model
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# 9️⃣ Evaluate
y_pred = model.predict(X_test)
print("R2 Score:", r2_score(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))

# 🔟 Save model
with open("CarPriceModel.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved as CarPriceModel.pkl")
