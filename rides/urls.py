from django.urls import path
from .views import RideListView, MakeRideView, submitRide

urlpatterns = [

    path('', RideListView.as_view(), name='rides'),
    path ('/make_ride', MakeRideView.as_view(), name = 'make_ride'),
    path ('submit_ride', submitRide, name = 'submit_ride' )
]