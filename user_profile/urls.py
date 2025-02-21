from django.urls import path
from .views import UserProfileView

app_name = 'user_profile'

urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),
]