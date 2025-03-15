import os
import json
import random
import pandas as pd

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def recommend_stocks(request):
    """
    POST endpoint that accepts JSON payload with keys:
      - age
      - income
      - investment_period
    and returns a JSON response with the top 5 recommended stocks.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed."}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON input."}, status=400)
    
    # Retrieve and validate inputs
    age = data.get("age")
    income = data.get("income")
    investment_period = data.get("investment_period")
    
    if age is None or income is None or investment_period is None:
        return JsonResponse({"error": "Missing required fields: age, income, and investment_period."}, status=400)
    
    try:
        age = int(age)
        income = float(income)
        investment_period = int(investment_period)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid data types provided."}, status=400)
    
    # Determine the desired distribution based on age:
    if age >= 50:
        distribution = {"Low": 5}  # 100% low volatility
    elif 40 <= age < 50:
        distribution = {"Low": 4, "Mid": 1}  # 80% low, 20% mid
    elif 30 <= age < 40:
        distribution = {"Low": 3, "Mid": 2}  # 50% low, 50% mid
    elif 20 <= age < 30:
        distribution = {"Mid": 4, "High": 1}  # 80% mid, 20% high
    else:
        distribution = {"Mid": 4, "High": 1}  # Default to 20s logic

    # Correct CSV file path based on actual location
    csv_path = "data\stocks_output.csv"

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return JsonResponse({"error": f"Error loading CSV file: {str(e)}"}, status=500)
    
    # Normalize the volatility column for consistency
    df["volatility"] = df["volatility"].astype(str).str.strip().str.title()
    
    recommendations = []

    # Fetch required stocks based on distribution
    for vol, count in distribution.items():
        df_cat = df[df["volatility"] == vol]
        available = len(df_cat)
        if available == 0:
            continue
        if available >= count:
            sampled = df_cat.sample(n=count)
        else:
            sampled = df_cat
        recommendations.extend(sampled.to_dict(orient="records"))
    
    # Fill up to 5 if needed
    if len(recommendations) < 5:
        selected_tickers = {rec["ticker"] for rec in recommendations if "ticker" in rec}
        remaining_df = df[~df["ticker"].isin(selected_tickers)]
        needed = 5 - len(recommendations)
        if not remaining_df.empty:
            if len(remaining_df) >= needed:
                extra = remaining_df.sample(n=needed)
            else:
                extra = remaining_df
            recommendations.extend(extra.to_dict(orient="records"))

    recommendations = recommendations[:5]

    return JsonResponse({"recommended_stocks": recommendations}, safe=False)
