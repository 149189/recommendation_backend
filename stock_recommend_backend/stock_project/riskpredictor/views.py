# riskpredictor/views.py
import os
import pickle
import json
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Load the pre-trained model (this happens once when the module is imported)
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

def calculate_bmi(weight, height):
    """
    Calculate BMI from weight (in kg) and height (in cm).
    """
    height_m = height / 100.0  # Convert height to meters
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)

@csrf_exempt  # For simplicity; ensure proper CSRF protection in production.
def predict_risk(request):
    """
    Accepts a POST request with JSON body containing user details and calculates risk.
    
    Example JSON payload:
    {
        "age": 45,
        "gender": "Male",
        "height": 175,
        "weight": 80,
        "smoking_status": "Yes",
        "cigarettes_per_day": 10,
        "alcohol_consumption": "Occasionally",
        "physical_activity": "Moderate",
        "dietary_habits": "Balanced",
        "occupation": "Office Job"
    }
    
    The BMI is automatically calculated from the provided height and weight.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)
    
    try:
        # Parse the JSON input
        data = json.loads(request.body.decode('utf-8'))
        age = data.get('age')
        gender = data.get('gender')
        height = data.get('height')  # in cm
        weight = data.get('weight')  # in kg
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

        # Create a DataFrame with the input data and the calculated BMI
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

        # Use the preloaded model to predict the risk percentage
        risk_percentage = model.predict(input_data)[0]

        return JsonResponse({
            'bmi': bmi,
            'risk_percentage': risk_percentage
                            }, status=200)

    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
