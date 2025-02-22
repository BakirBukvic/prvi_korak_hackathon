from django.shortcuts import render, redirect
from django.views.generic import ListView
from base.models import Ride
from django.views.generic import CreateView
from django.db.models import Count
from django.views.generic import ListView
from django.views.generic import CreateView
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import re

from django.db.models import Count, Q
from django.urls import reverse
class RideListView(ListView):
    model = Ride
    template_name = 'rides.html'
    context_object_name = 'rides'

    def get_queryset(self):
        # Annotate each ride with applicant count
        return Ride.objects.annotate(
            applicant_count=Count('applications'),
            pending_count=Count('applications', filter=Q(applications__status='PENDING')),
            approved_count=Count('applications', filter=Q(applications__status='APPROVED'))
        ).order_by('-created_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add application stats for each ride
        for ride in context['rides']:
            print(f"Ride {ride.id}: {ride.applicant_count} applicants "
                  f"({ride.pending_count} pending, {ride.approved_count} approved)")
            
        return context

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
    ride.save()
    return ride



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





from base.models import UserRideAssociation


def submitRide(request):
    if request.method == 'POST':
        try:
            # Create the ride first
            ride = create_ride_from_post_data(request.POST)
            
            # Create UserRideAssociation for the driver
            UserRideAssociation.objects.create(
                user=request.user,
                ride=ride,
                is_driver=True,

            )
            
            return redirect(reverse('rides'))
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

from django.views.generic import DetailView


from django.views.generic import DetailView
from django.db.models import Count, Q

class ApplyForRideView(DetailView):
    model = Ride
    template_name = 'apply.html'
    context_object_name = 'ride'
    pk_url_kwarg = 'ride_id'

    def get_object(self):
        # Get the ride and annotate with application counts
        return Ride.objects.annotate(
            applicant_count=Count('applications'),
            pending_count=Count('applications', filter=Q(applications__status='PENDING')),
            approved_count=Count('applications', filter=Q(applications__status='APPROVED'))
        ).get(pk=self.kwargs['ride_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ride = self.get_object()
        
        # Debug prints to verify counts
        print(f"DEBUG: Ride ID: {ride.id}")
        print(f"DEBUG: Applicant count: {ride.applicant_count}")
        print(f"DEBUG: Pending count: {ride.pending_count}")
        print(f"DEBUG: Approved count: {ride.approved_count}")
        
        # Get driver info
        driver_association = ride.riders.filter(is_driver=True).first()
        if driver_association:
            context['driver'] = driver_association.user
        else:
            context['driver'] = None
            
        return context
    
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse



@login_required
def join_ride(request, ride_id):
    if request.method == 'POST':
        try:
            ride = get_object_or_404(Ride, id=ride_id)
            
            # Check if user is already in the ride
            if UserRideAssociation.objects.filter(user=request.user, ride=ride).exists():
                return JsonResponse({'success': False, 'error': 'You are already part of this ride'})
            
            # Check if there are available seats
            current_riders = UserRideAssociation.objects.filter(ride=ride).count()
            if current_riders >= ride.travelers:
                return JsonResponse({'success': False, 'error': 'No available seats'})
            
            # Create association
            UserRideAssociation.objects.create(
                user=request.user,
                ride=ride,
                is_driver=False
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'})