from django.urls import path
from .views import base

app_name = 'base'

urlpatterns = [
    path('', base, name='index'),
]