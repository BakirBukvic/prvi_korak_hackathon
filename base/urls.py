from django.urls import path
from .views import base
from login.views import UserLogoutView
app_name = 'base'

urlpatterns = [
    path('', base, name='index'),
        path('logout/', UserLogoutView.as_view(), name='logout'),
]