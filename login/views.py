from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('racuni:index')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login:login')
    http_method_names = ['get', 'post']  # Allow both GET and POST methods