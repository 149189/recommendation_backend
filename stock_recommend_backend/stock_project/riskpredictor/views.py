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
    """Calculate BMI from weight (kg) and height (cm)."""
    height_m = height / 100.0  # Convert height to meters
    return weight / (height_m ** 2)

@csrf_exempt  # For simplicity, disable CSRF (consider security implications in production)
def predict_risk(request):
    """
    Accepts a POST request with the following JSON body:
    
    {
        "age": int,
        "gender": "Male" | "Female" | "Other" | "Prefer not to say",
        "height": float,          # in centimeters
        "weight": float,          # in kilograms
        "smoking_status": "Yes" | "No",
        "cigarettes_per_day": int,  # if smoking_status is "Yes"
        "alcohol_consumption": "Never" | "Occasionally" | "Frequently" | "Daily",
        "physical_activity": "Sedentary" | "Moderate" | "Active" | "Very Active",
        "dietary_habits": "Healthy" | "Balanced" | "Unhealthy" | "Junk Food Regularly",
        "occupation": string
    }
    
    It returns a JSON response with the predicted risk percentage.
    """
    if request.method == 'POST':
        try:
            # Parse JSON input
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

            # Create a DataFrame with the input data
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

            # Use the model to predict the risk percentage
            risk_percentage = model.predict(input_data)[0]

            return JsonResponse({'risk_percentage': risk_percentage}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)
