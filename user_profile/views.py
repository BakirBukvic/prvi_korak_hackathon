from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
import os
import random
from django.conf import settings

from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
import random
from django.conf import settings
from base.models import RideApplication, UserRideAssociation, Ride
from django.http import JsonResponse  # Add this import
from django.utils import timezone
from django.db.models import Count, Q, F

def calculate_penguins_saved(distance):
    # Divide distance by 83 and round to 2 decimal places
        return round(distance / 83, 2)

def get_random_penguin():
    try:
        # Use BASE_DIR from settings to ensure correct path
        base_dir = settings.BASE_DIR
        penguin_dir = os.path.join(base_dir, 'base', 'static', 'base', 'penguin_images')
        # Create directory if it doesn't exist
        os.makedirs(penguin_dir, exist_ok=True)
        images = os.listdir(penguin_dir)
        if not images:
            # Return a default image name if no images exist
            return 'default_penguin.jpg'
        return random.choice(images)
    except Exception as e:
        # Return a default image name in case of any error
        return 'default_penguin.jpg'


class UserProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'user_profile.html'
    context_object_name = 'user_profile'


  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['penguins_saved'] = calculate_penguins_saved(user.km_passed)
        context['random_penguin'] = get_random_penguin()
        return context
    
    def get_object(self, queryset=None):
        return self.request.user
    


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from base.models import RideApplication, UserRideAssociation

@login_required
def pendingRides(request):
    # Get all rides where the user is the driver
    user_rides = UserRideAssociation.objects.filter(
        user=request.user,
        is_driver=True
    ).values_list('ride', flat=True)

    # Get pending applications for those rides
    pending_applications = RideApplication.objects.filter(
        ride__in=user_rides,
        status='PENDING'
    ).select_related('user', 'ride')

    context = {
        'pending_applications': pending_applications
    }
    
    return render(request, 'pending_rides.html', context)
     

@login_required
def sent_rides(request):
    # Get all applications for the current user
    ride_applications = RideApplication.objects.filter(
        user=request.user
    ).select_related('ride').order_by('-applied_at')
    
    return render(request, 'sent_rides.html', {
        'ride_applications': ride_applications
    })

@login_required
def cancel_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RideApplication, 
                                      id=application_id, 
                                      user=request.user, 
                                      status='PENDING')
        application.delete()
        messages.success(request, 'Application cancelled successfully')
        return redirect('user_profile:sent_rides')
    

@login_required
def approve_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RideApplication, id=application_id)
        
        # Check if the current user is the driver through UserRideAssociation
        is_driver = UserRideAssociation.objects.filter(
            user=request.user,
            ride=application.ride,
            is_driver=True
        ).exists()
        
        if is_driver:
            # Check if there are available seats
            ride = application.ride
            if ride.travelers <= 0:
                messages.error(request, 'No more seats available for this ride.')
                return redirect('user_profile:pending_rides')
            
            # Update application status and decrease available passengers
            application.status = 'APPROVED'
            ride.travelers -= 1
            
            # Save both objects
            application.save()
            ride.save()
            
            messages.success(request, f'Application for {application.user.username} has been approved.')
        else:
            messages.error(request, 'You do not have permission to approve this application.')
            
    return redirect('user_profile:pending_rides')
@login_required
def reject_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RideApplication, id=application_id)
        
        # Check if the current user is the driver through UserRideAssociation
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


@login_required
def rides(request):
    now = timezone.now()
    user = request.user

    # Get rides where user is the driver
    user_rides = Ride.objects.filter(
        riders__user=user,
        riders__is_driver=True
    ).annotate(
        approved_count=Count('riders', filter=Q(riders__is_driver=False)),
        initial_travelers=F('travelers')
    ).prefetch_related('riders__user')

    # Future rides: Either future date OR 'PREPARING' status
    future_rides = user_rides.filter(
        Q(start_date__gt=now) | Q(status='PREPARING')
    ).order_by('start_date')
    
    # Past rides: Only include rides with 'FINISHED' status
    past_rides = user_rides.filter(
        status='FINISHED'  # Remove the start_date condition
    ).order_by('-start_date')

    context = {
        'future_rides': future_rides,
        'past_rides': past_rides,
        'user': user
    }
    
    return render(request, 'my_rides.html', context)
    
@login_required
def remove_passenger(request, ride_id, user_id):
    if request.method == 'POST':
        ride = get_object_or_404(Ride, 
            id=ride_id, 
            riders__user=request.user, 
            riders__is_driver=True
        )
        
        # Get the association to remove
        association = get_object_or_404(UserRideAssociation, 
            ride=ride,
            user_id=user_id,
            is_driver=False
        )
        
        # Remove the passenger
        association.delete()
        
        # Increase available seats
        ride.travelers += 1
        ride.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})