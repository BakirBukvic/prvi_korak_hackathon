from django.urls import path
from .views import UserProfileView, pendingRides

app_name = 'user_profile'

urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),
     path('sent_rides', UserProfileView.as_view(), name='sent_rides'),
      path('pending_rides', pendingRides, name='pending_rides'),
]