from django.urls import path
from .views import UserProfileView, pendingRides, sent_rides, cancel_application, approve_application, reject_application

app_name = 'user_profile'

urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),
    path('sent_rides/', sent_rides, name='sent_rides'),
    path('cancel_application/<int:application_id>/', cancel_application, name='cancel_application'),
    path('pending_rides/', pendingRides, name='pending_rides'),
    path('approve_application/<int:application_id>/', approve_application, name='approve_application'),  # Remove the hyphen
    path('reject_application/<int:application_id>/', reject_application, name='reject_application')      # Remove the hyphen
]