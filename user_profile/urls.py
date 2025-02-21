from django.urls import path
from .views import userProfile

app_name = 'user_profile'

urlpatterns = [
    path('', userProfile, name='profile'),
]