# ai_analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze, name='analyze'),
    path('news/', views.news_sentiment, name='news_sentiment'),
    path('historical/', views.historical_analysis, name='historical_analysis'),
]
