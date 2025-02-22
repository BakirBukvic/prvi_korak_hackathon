from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm
from base.models import UserLevel
from django.views.generic.edit import CreateView
from django.contrib.auth import logout

class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('racuni:index')

from django.shortcuts import redirect
from django.views import View
from django.contrib.auth import logout

# Replace the LogoutView with a custom View
class UserLogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect('/')  # Redirect to home page
        response.delete_cookie('sessionid')
        return response

class UserRegistrationView(CreateView):
    template_name = 'register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login:login')
    
    def form_valid(self, form):
        # Get or create the default UserLevel
        default_level, created = UserLevel.objects.get_or_create(
            name='Beginner',
            defaults={
                'description': 'Starting level for new users',
                'points': 0,
                'level': 1
            }
        )
        
        # Save the user instance
        response = super().form_valid(form)
        
        # Set the default level for the new user
        self.object.level = default_level
        self.object.save()
        
        return response