from django.urls import path
from .views import recommend_stocks, json_to_csv

urlpatterns = [
    path('recommend/', recommend_stocks, name='recommend_stocks'),
     path('convert_json_to_csv/', json_to_csv, name='json_to_csv'),
]
