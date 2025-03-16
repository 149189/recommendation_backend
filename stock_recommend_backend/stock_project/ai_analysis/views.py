# ai_analysis/views.py
from django.http import JsonResponse
from .analysis import run_market_trend_analysis, analyze_news_sentiment, analyze_historical_data

def analyze(request):
    # Trigger the market trends analysis
    analysis_results = run_market_trend_analysis()
    return JsonResponse(analysis_results)

def news_sentiment(request):
    # Run and return only news sentiment analysis
    sentiment = analyze_news_sentiment()
    return JsonResponse({"news_sentiment": sentiment})

def historical_analysis(request):
    # Run and return only historical data analysis
    trend_indicator = analyze_historical_data()
    return JsonResponse({"trend_indicator": trend_indicator})