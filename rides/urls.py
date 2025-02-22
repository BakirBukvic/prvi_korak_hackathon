from django.urls import path
from .views import RideListView, MakeRideView

urlpatterns = [

    path('', RideListView.as_view(), name='rides'),
    path ('/make_ride', MakeRideView.as_view(), name = 'make_ride'),
]