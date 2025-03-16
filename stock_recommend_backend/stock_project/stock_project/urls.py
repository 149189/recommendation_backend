from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('stock_app.urls')),
    path('risk/', include('riskpredictor.urls')),
    path('ai/', include('ai_analysis.urls')),        # API endpoints under /api/
]
