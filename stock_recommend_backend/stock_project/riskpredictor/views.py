# riskpredictor/views.py
import os
import pickle
import json
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Load the pre-trained ML model (model.pkl should be in the same directory as views.py)
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# Load the insurance product suggestions from JSON file
PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), 'insurance_products.json')
with open(PRODUCTS_PATH, 'r') as f:
    INSURANCE_PRODUCTS = json.load(f)

def calculate_bmi(weight, height):
    """
    Calculate BMI from weight (in kg) and height (in cm).
    """
    height_m = height / 100.0  # convert cm to meters
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)

def get_risk_band(risk_percentage):
    """
    Determine the risk band based on the predicted risk percentage.
    """
    if risk_percentage <= 30:
        return 'low'
    elif risk_percentage <= 70:
        return 'medium'
    else:
        return 'high'

@csrf_exempt  # For demonstration; ensure proper CSRF handling in production.
def predict_risk(request):
    """
    API Endpoint to predict insurance risk percentage and recommend insurance products.

    Expected JSON Payload:
    {
        "age": int,
        "gender": "Male" | "Female" | "Other" | "Prefer not to say",
        "height": float,          # in centimeters
        "weight": float,          # in kilograms
        "smoking_status": "Yes" | "No",
        "cigarettes_per_day": int, # if smoking_status is "Yes"
        "alcohol_consumption": "Never" | "Occasionally" | "Frequently" | "Daily",
        "physical_activity": "Sedentary" | "Moderate" | "Active" | "Very Active",
        "dietary_habits": "Healthy" | "Balanced" | "Unhealthy" | "Junk Food Regularly",
        "occupation": string
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)

    try:
        # Parse incoming JSON payload
        data = json.loads(request.body.decode('utf-8'))
        age = data.get('age')
        gender = data.get('gender')
        height = data.get('height')
        weight = data.get('weight')
        smoking_status = data.get('smoking_status')
        cigarettes_per_day = data.get('cigarettes_per_day', 0)
        alcohol_consumption = data.get('alcohol_consumption')
        physical_activity = data.get('physical_activity')
        dietary_habits = data.get('dietary_habits')
        occupation = data.get('occupation')

        # Validate required fields
        if None in [age, gender, height, weight, smoking_status, alcohol_consumption, physical_activity, dietary_habits, occupation]:
            return JsonResponse({'error': 'Missing required input fields.'}, status=400)

        # Calculate BMI
        bmi = calculate_bmi(weight, height)

        # Prepare the input data for the ML model
        input_data = pd.DataFrame({
            'Age': [age],
            'Gender': [gender],
            'Height (cm)': [height],
            'Weight (kg)': [weight],
            'Smoking Status': [smoking_status],
            'Cigarettes per day': [cigarettes_per_day],
            'Alcohol Consumption': [alcohol_consumption],
            'Physical Activity Level': [physical_activity],
            'Dietary Habits': [dietary_habits],
            'Occupation': [occupation],
            'BMI': [bmi]
        })

        # Predict risk percentage using the ML model
        risk_percentage = model.predict(input_data)[0]
        risk_band = get_risk_band(risk_percentage)

        # Fetch the recommended insurance products from the loaded JSON based on the risk band
        recommended_products = INSURANCE_PRODUCTS.get(risk_band, [])

        # Build and return the JSON response
        response = {
            'bmi': bmi,
            'risk_percentage': risk_percentage,
            'risk_band': risk_band
        }
        return JsonResponse(response, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
