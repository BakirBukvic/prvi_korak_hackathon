from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
import os
import random
from django.conf import settings

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
     