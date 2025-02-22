from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm
from base.models import UserLevel
from django.views.generic.edit import CreateView


class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('racuni:index')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login:login')
    http_method_names = ['get', 'post']  # Allow both GET and POST methods

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