import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_iris
import joblib
import json
import os

mlflow.set_experiment("milestone3_experiment")

data = load_iris()
X = data.data
y = data.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

with mlflow.start_run():

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    mlflow.log_metric("accuracy", accuracy)

    os.makedirs("outputs", exist_ok=True)

    joblib.dump(model, "outputs/model.pkl")

    with open("outputs/metrics.json", "w") as f:
        json.dump({"accuracy": accuracy}, f)

    mlflow.sklearn.log_model(model, "model")

    print("Accuracy:", accuracy)