import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib
import os
import numpy as np

def train_and_save_model():
    # Generate synthetic dataset with new features
    data = {
        "distance": [10, 20, 30, 40, 50, 15, 25, 35, 45, 55],
        "fuel_efficiency": [5, 6, 7, 8, 9, 5.5, 6.5, 7.5, 8.5, 9.5],
        "transport_mode": ["car", "car", "car", "car", "car", "bike", "bike", "bike", "bike", "bike"],
        "weather": ["clear", "rainy", "clear", "rainy", "snowy", "clear", "rainy", "clear", "rainy", "snowy"],
        "traffic_intensity": ["low", "high", "medium", "high", "low", "medium", "high", "low", "medium", "high"],
        "road_type": ["city", "highway", "city", "highway", "city", "highway", "city", "highway", "city", "highway"],
        "emission": [2, 4.5, 6, 9, 11, 0.5, 1.2, 0.9, 1.5, 2.0]
    }
    df = pd.DataFrame(data)

    # One-hot encode categorical features
    df = pd.get_dummies(df, columns=["transport_mode", "weather", "traffic_intensity", "road_type"], drop_first=True)

    feature_cols = [col for col in df.columns if col != "emission"]
    X = df[feature_cols]
    y = df["emission"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Calculate error metrics
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    print(f"Model RMSE: {rmse:.3f}")

    # Save the trained model
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, "model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()


