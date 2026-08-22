# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from pathlib import Path
from flask import Flask, request, jsonify  # For creating the Flask API

app = Flask(__name__)
MODEL_PATH = Path(__file__).with_name("superkart_sales_pipeline_v1_0.joblib")
model = joblib.load(MODEL_PATH)
PERISHABLES = {"Dairy", "Meat", "Fruits and Vegetables", "Breakfast", "Breads", "Seafood"}
FIELDS = [
    "Product_Id", "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area",
    "Product_Type", "Product_MRP", "Store_Establishment_Year", "Store_Size",
    "Store_Location_City_Type", "Store_Type",
]

def prepare_record(payload):
    missing = [field for field in FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    sugar = "Regular" if payload["Product_Sugar_Content"] == "reg" else payload["Product_Sugar_Content"]
    row = {
        "Product_Weight": float(payload["Product_Weight"]),
        "Product_Sugar_Content": sugar,
        "Product_Allocated_Area": float(payload["Product_Allocated_Area"]),
        "Product_Type": str(payload["Product_Type"]),
        "Product_MRP": float(payload["Product_MRP"]),
        "Store_Size": str(payload["Store_Size"]),
        "Store_Location_City_Type": str(payload["Store_Location_City_Type"]),
        "Store_Type": str(payload["Store_Type"]),
        "Product_Id_Prefix": str(payload["Product_Id"])[:2],
        "Store_Age_Years": 2026 - int(payload["Store_Establishment_Year"]),
        "Product_Type_Category": "Perishable" if payload["Product_Type"] in PERISHABLES else "Non-Perishable",
    }
    if row["Store_Age_Years"] < 0:
        raise ValueError("Store_Establishment_Year cannot be beyond 2026")
    return pd.DataFrame([row])

# Define a route for the home page (GET request)
@app.get("/")
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return jsonify(service="Welcome to the SuperKart Sales Forecast API", version="1.0", status="ok")

# Define an endpoint for single sales prediction (POST request)
@app.post("/v1/predict")
def predict_sales():
    """
    This function handles POST requests to the '/v1/predict' endpoint.
    It expects a JSON payload containing store/product details and returns
    the predicted sales as a JSON response.
    """
    try:
        payload = request.get_json()
        record = model.predict(prepare_record(payload))[0]
        prediction = max(0.0, float(record))
        return jsonify(
            predicted_sales=round(prediction, 2),
            model_version="1.0",
        )
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify(error=str(exc)), 400
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify(error="Prediction failed"), 500

# Run the Flask application in debug mode if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
