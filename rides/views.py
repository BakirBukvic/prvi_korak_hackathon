from django.shortcuts import render
from django.views.generic import ListView
from base.models import Ride
from django.views.generic import CreateView


class RideListView(ListView):
    model = Ride
    template_name = 'rides.html'
    context_object_name = 'rides'
    ordering = ['-created_on']  # Orders by newest first


class MakeRideView(CreateView):
    model = Ride
    template_name = 'make_ride.html'
    fields = ['start_date', 'distance', 'duration', 'travelers']


    