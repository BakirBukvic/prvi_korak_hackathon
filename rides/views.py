from django.shortcuts import render, redirect
from django.views.generic import ListView
from base.models import Ride, RouteDetails
from django.views.generic import CreateView

from django.views.generic import ListView
from django.views.generic import CreateView
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import re
from django.urls import reverse

class RideListView(ListView):
    model = Ride
    template_name = 'rides.html'
    context_object_name = 'rides'
    ordering = ['-created_on']  # Orders by newest first


class MakeRideView(CreateView):
    model = Ride
    template_name = 'make_ride.html'
    fields = ['start_date', 'distance', 'duration', 'travelers']


def create_ride_from_post_data(post_data):
    # Parse duration string (e.g. "2 hours 30 mins" to timedelta)
    duration_str = post_data.get('duration_text', '')
    duration = parse_duration_string(duration_str)

    # Create a new ride object
    ride = Ride(
        start=post_data.get('origin'),
        end=post_data.get('destination'), 
        distance=post_data.get('distance_km'),
        duration=duration,
        travelers=post_data.get('travelers'),
        created_on=timezone.now(),
        start_date=timezone.now(),
        arriving_date=timezone.now()
    )
    ride.save()
    return ride

def create_ride_details_from_post_data(post_data, ride):
    """
    Creates a RouteDetails instance from POST data and associates it with a ride
    Args:
        post_data: The POST request data
        ride: The Ride instance to associate with
    Returns:
        RouteDetails instance
    """
    route_details = RouteDetails(
        ride=ride,
        origin_place_id=post_data.get('origin_place_id'),
        origin_latitude=float(post_data.get('origin_latitude')),
        origin_longitude=float(post_data.get('origin_longitude')),
        destination_place_id=post_data.get('destination_place_id'),
        destination_latitude=float(post_data.get('destination_latitude')),
        destination_longitude=float(post_data.get('destination_longitude')),
        distance_km=float(post_data.get('distance_km')),
        duration_text=post_data.get('duration_text'),
        selected_route_index=int(post_data.get('selected_route_index')),
        selected_route_polyline=post_data.get('selected_route_polyline')
    )
    route_details.save()
    return route_details



def parse_duration_string(duration_str):
    # Extract hours and minutes from strings like "2 hours 30 mins"
    hours = 0
    minutes = 0
    
    hour_match = re.search(r'(\d+)\s*hour', duration_str)
    if hour_match:
        hours = int(hour_match.group(1))
        
    min_match = re.search(r'(\d+)\s*min', duration_str)
    if min_match:
        minutes = int(min_match.group(1))
        
    return timedelta(hours=hours, minutes=minutes)




def submitRide(request):
    if request.method == 'POST':
        try:
            # Create the ride first
            ride = create_ride_from_post_data(request.POST)
            # Create the route details and associate with the ride
            route_details = create_ride_details_from_post_data(request.POST, ride)
            return redirect(reverse('rides'))
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    