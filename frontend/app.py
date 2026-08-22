import os
import requests
import streamlit as st

# Base URL of the Flask backend
BACKEND_URL = "http://backend:7860"

st.set_page_config(page_title="SuperKart Sales Forecaster", layout="centered")
st.title("SuperKart Sales Forecaster")
st.caption("Estimate store revenue for inventory and scenario planning.")
st.subheader("Enter the details needed for forecasting:")

PRODUCT_TYPES = [
    "Baking Goods", "Breads", "Breakfast", "Canned", "Dairy", "Frozen Foods",
    "Fruits and Vegetables", "Hard Drinks", "Health and Hygiene", "Household",
    "Meat", "Others", "Seafood", "Snack Foods", "Soft Drinks", "Starchy Foods",
]

with st.form("forecast_form"):
    col1, col2 = st.columns(2)
    with col1:
        product_id = st.text_input("Product ID", value="FD6114", max_chars=10)
        product_weight = st.number_input("Product weight", min_value=0.01, value=12.66, step=0.1)
        sugar = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
        area = st.number_input("Allocated area ratio", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f")
        product_type = st.selectbox("Product type", PRODUCT_TYPES)
    with col2:
        mrp = st.number_input("Product MRP", min_value=0.01, value=117.08, step=1.0)
        establishment_year = st.number_input("Store establishment year", min_value=1900, max_value=2026, value=2009, step=1)
        store_size = st.selectbox("Store size", ["Small", "Medium", "High"], index=1)
        city_type = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3"], index=1)
        store_type = st.selectbox("Store type", ["Departmental Store", "Food Mart", "Supermarket Type1", "Supermarket Type2"], index=3)
    submitted = st.form_submit_button("Forecast sales", type="primary", use_container_width=True)

if submitted:
    payload = {
        "Product_Id": product_id, "Product_Weight": product_weight,
        "Product_Sugar_Content": sugar, "Product_Allocated_Area": area,
        "Product_Type": product_type, "Product_MRP": mrp,
        "Store_Establishment_Year": establishment_year, "Store_Size": store_size,
        "Store_Location_City_Type": city_type, "Store_Type": store_type,
    }

    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=20)
        if response.status_code == 200:
          result = response.json()
          st.success(f"Predicted product-store sales:{result['predicted_sales']}")
          st.caption(f"Model version {result['model_version']}.")
        else:
          st.error("Unable to connect to the prediction API.")
    except requests.RequestException as ex:
        st.error(f"Forecast service unavailable: {ex}")
