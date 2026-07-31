from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    ('register/', RegisterView.as_view()),
    ('login/', TokenObtainPairView.as_view()),
    ('refresh/', TokenRefreshView.as_view())
]
