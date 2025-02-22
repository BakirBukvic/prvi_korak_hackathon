from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, F, Prefetch, Subquery, OuterRef, BooleanField, When, Case
from base.models import RideApplication, UserRideAssociation, Ride
import os
import random
from django.conf import settings

def calculate_penguins_saved(distance):
    return round(distance / 83, 2)

def get_random_penguin():
    try:
        base_dir = settings.BASE_DIR
        penguin_dir = os.path.join(base_dir, 'base', 'static', 'base', 'penguin_images')
        os.makedirs(penguin_dir, exist_ok=True)
        images = os.listdir(penguin_dir)
        return random.choice(images) if images else 'default_penguin.jpg'
    except Exception:
        return 'default_penguin.jpg'

class UserProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'user_profile.html'
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # Add basic profile data
        context['penguins_saved'] = calculate_penguins_saved(user.km_passed)
        context['random_penguin'] = get_random_penguin()

        # Define prefetches for efficiency
        approved_applications = Prefetch(
            'applications',
            queryset=RideApplication.objects.filter(status='APPROVED').select_related('user'),
            to_attr='approved_passengers'
        )
        driver_prefetch = Prefetch(
            'riders',
            queryset=UserRideAssociation.objects.filter(is_driver=True).select_related('user'),
            to_attr='driver_association'
        )

        # Subquery to determine if the user is the driver for each ride
        user_association = UserRideAssociation.objects.filter(
            ride=OuterRef('pk'),
            user=user
        ).values('is_driver')[:1]

        # Fetch all rides where the user is associated (driver or passenger)
        user_rides = Ride.objects.filter(
            riders__user=user
        ).annotate(
            is_driver=Subquery(user_association, output_field=BooleanField()),
            approved_count=Count('applications', filter=Q(applications__status='APPROVED')),
            initial_travelers=F('travelers')
        ).prefetch_related(approved_applications, driver_prefetch, 'riders__user')

        # Split into future and past rides
        context['future_rides'] = user_rides.filter(status='PREPARING').order_by('start_date')
        context['past_rides'] = user_rides.filter(~Q(status='PREPARING')).order_by('-start_date')

        # Pending Rides tab data
        user_rides_ids = UserRideAssociation.objects.filter(
            user=user,
            is_driver=True
        ).values_list('ride', flat=True)
        context['pending_applications'] = RideApplication.objects.filter(
            ride__in=user_rides_ids,
            status='PENDING'
        ).select_related('user', 'ride')

        # Sent Rides tab data
        context['ride_applications'] = RideApplication.objects.filter(
            user=user
        ).select_related('ride').order_by('-applied_at')

        return context

    def get_object(self, queryset=None):
        return self.request.user

# Supporting view functions (unchanged from original, included for completeness)

def pendingRides(request):
    user_rides = UserRideAssociation.objects.filter(
        user=request.user,
        is_driver=True
    ).values_list('ride', flat=True)
    pending_applications = RideApplication.objects.filter(
        ride__in=user_rides,
        status='PENDING'
    ).select_related('user', 'ride')
    return render(request, 'pending_rides.html', {'pending_applications': pending_applications})

def sent_rides(request):
    ride_applications = RideApplication.objects.filter(
        user=request.user
    ).select_related('ride').order_by('-applied_at')
    return render(request, 'sent_rides.html', {'ride_applications': ride_applications})

def cancel_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RideApplication, id=application_id, user=request.user, status='PENDING')
        application.delete()
        messages.success(request, 'Application cancelled successfully')
        return redirect('user_profile:sent_rides')
    return redirect('user_profile')


def approve_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RideApplication, id=application_id)
        is_driver = UserRideAssociation.objects.filter(
            user=request.user,
            ride=application.ride,
            is_driver=True
        ).exists()
        if is_driver:
            ride = application.ride
            if ride.travelers <= 0:
                messages.error(request, 'No more seats available for this ride.')
                return redirect('user_profile:pending_rides')
            application.status = 'APPROVED'
            ride.travelers -= 1
            application.save()
            ride.save()
            
            # Create UserRideAssociation for the passenger if it doesn't exist
            UserRideAssociation.objects.get_or_create(
                user=application.user,
                ride=ride,
                defaults={'is_driver': False}
            )
            
            messages.success(request, f'Application for {application.user.username} has been approved.')
        else:
            messages.error(request, 'You do not have permission to approve this application.')
    return redirect('user_profile')

def reject_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RideApplication, id=application_id)
        is_driver = UserRideAssociation.objects.filter(
            user=request.user,
            ride=application.ride,
            is_driver=True
        ).exists()
        if is_driver:
            application.status = 'REJECTED'
            application.save()
            messages.success(request, f'Application for {application.user.username} has been rejected.')
        else:
            messages.error(request, 'You do not have permission to reject this application.')
    return redirect('user_profile:pending_rides')


def rides(request):
    now = timezone.now()
    user = request.user
    approved_applications = Prefetch(
        'applications',
        queryset=RideApplication.objects.filter(status='APPROVED').select_related('user'),
        to_attr='approved_passengers'
    )
    user_rides = Ride.objects.filter(
        riders__user=user
    ).annotate(
        is_driver=Case(
            When(riders__user=user, riders__is_driver=True, then=True),
            default=False,
            output_field=BooleanField()
        ),
    approved_count=Count('applications', filter=Q(applications__status='APPROVED')),
    initial_travelers=F('travelers')
).prefetch_related(approved_applications, 'riders__user')
    future_rides = user_rides.filter(status='PREPARING').order_by('start_date')
    past_rides = user_rides.filter(~Q(status='PREPARING')).order_by('-start_date')
    context = {'future_rides': future_rides, 'past_rides': past_rides, 'user': user}
    return render(request, 'my_rides.html', context)

def remove_passenger(request, ride_id, user_id):
    if request.method == 'POST':
        ride = get_object_or_404(Ride, id=ride_id, riders__user=request.user, riders__is_driver=True)
        association = get_object_or_404(UserRideAssociation, ride=ride, user_id=user_id, is_driver=False)
        association.delete()
        ride.travelers += 1
        ride.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def cancel_ride(request, ride_id):
    if request.method == 'POST':
        try:
            ride = get_object_or_404(Ride, id=ride_id, riders__user=request.user, riders__is_driver=True)
            if ride.status == 'PREPARING':
                ride.status = 'CANCELED'
                ride.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Can only cancel rides in PREPARING status'})
        except Ride.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ride not found or you are not the driver'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def delete_ride(request, ride_id):
    if request.method == 'POST':
        try:
            ride = get_object_or_404(Ride, id=ride_id, riders__user=request.user, riders__is_driver=True)
            ride.delete()
            return JsonResponse({'success': True})
        except Ride.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ride not found or you are not the driver'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def leave_ride(request, ride_id):
    if request.method == 'POST':
        try:
            # Get the ride and user association
            association = get_object_or_404(
                UserRideAssociation, 
                ride_id=ride_id,
                user=request.user,
                is_driver=False  # Only passengers can leave
            )
            
            # Get the ride
            ride = association.ride
            
            # Delete the association
            association.delete()
            
            # Increment available seats
            ride.travelers += 1
            ride.save()
            
            # Delete the application if it exists
            RideApplication.objects.filter(
                user=request.user,
                ride=ride
            ).delete()
            
            return JsonResponse({'success': True})
        except UserRideAssociation.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'You are not a passenger on this ride or the ride does not exist'
            })
    return JsonResponse({'success': False, 'error': 'Invalid request method'})