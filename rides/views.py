from django.shortcuts import render
from django.views.generic import ListView
from base.models import Ride

class RideListView(ListView):
    model = Ride
    template_name = 'rides.html'
    context_object_name = 'rides'
    ordering = ['-created_on']  # Orders by newest first