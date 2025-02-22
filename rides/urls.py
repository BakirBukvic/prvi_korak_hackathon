from django.urls import path
from .views import RideListView, MakeRideView, submitRide, ApplyForRideView,join_ride

urlpatterns = [

    path('', RideListView.as_view(), name='rides'),
    path ('/make_ride', MakeRideView.as_view(), name = 'make_ride'),
    path ('submit_ride', submitRide, name = 'submit_ride' ),
    path('apply_for_ride/<int:ride_id>/', ApplyForRideView.as_view(), name='apply_for_ride'),
    path('join_ride/<int:ride_id>/', join_ride, name='join_ride'),

]