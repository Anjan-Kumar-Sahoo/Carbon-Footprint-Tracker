import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
import os

def train_and_save_model():
    # Generate synthetic dataset
    data = {
        "distance": [10, 20, 30, 40, 50, 15, 25, 35, 45, 55],
        "fuel_efficiency": [5, 6, 7, 8, 9, 5.5, 6.5, 7.5, 8.5, 9.5],
        "transport_mode": ["car", "car", "car", "car", "car", "bike", "bike", "bike", "bike", "bike"],
        "emission": [2, 4, 6, 8, 10, 0.5, 0.7, 0.9, 1.1, 1.3]
    }
    df = pd.DataFrame(data)

    # Convert categorical to numerical (one-hot encoding)
    df = pd.get_dummies(df, columns=["transport_mode"], drop_first=True)

    X = df[["distance", "fuel_efficiency", "transport_mode_car"]]
    y = df["emission"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Save the trained model
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, "model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()


