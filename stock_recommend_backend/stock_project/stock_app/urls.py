from django.urls import path
from .views import recommend_stocks

urlpatterns = [
    path('recommend/', recommend_stocks, name='recommend_stocks'),
]
