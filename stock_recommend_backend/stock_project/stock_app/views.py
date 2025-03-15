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

import os
import json
import csv

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def parse_number(s):
    """Convert a string to a float after removing commas and spaces."""
    if not s:
        return None
    s = s.replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None

@csrf_exempt
def json_to_csv(request):
    """
    POST API endpoint that accepts JSON data, converts it to CSV format,
    and saves it in the `data/` folder in the Django backend.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed."}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON input."}, status=400)

    if not isinstance(data, list):
        return JsonResponse({"error": "Invalid data format. Expected a list of objects."}, status=400)

    output_rows = []
    dummy_counter = 1

    for record in data:
        symbol = record.get("symbol", "").strip()
        if not symbol:
            ticker = f"DUMMY{dummy_counter}"
            dummy_counter += 1
            company_name = f"Dummy Company {dummy_counter}"
        else:
            ticker = symbol
            company_name = symbol  # Assuming symbol as company name

        last_price = parse_number(record.get("lastPrice", ""))
        high = parse_number(record.get("high", ""))
        low = parse_number(record.get("low", ""))

        if last_price is None or high is None or low is None or last_price == 0:
            volatility = "Low"
        else:
            diff = high - low
            percent = (diff / last_price) * 100
            if percent < 1.5:
                volatility = "Low"
            elif percent < 3:
                volatility = "Mid"
            else:
                volatility = "High"

        output_rows.append({
            "ticker": ticker,
            "company_name": company_name,
            "volatility": volatility
        })

    # Define CSV file path inside `data/` folder
    csv_dir = os.path.join(settings.BASE_DIR, "stock_project", "data")
    os.makedirs(csv_dir, exist_ok=True)  # Ensure directory exists
    csv_file_path = os.path.join(csv_dir, "stocks_output.csv")

    # Write to CSV file
    with open(csv_file_path, "w", newline="") as csvfile:
        fieldnames = ["ticker", "company_name", "volatility"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)

    return JsonResponse({"message": f"CSV file saved successfully at {csv_file_path}"})
