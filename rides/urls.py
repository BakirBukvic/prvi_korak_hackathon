from django.urls import path
from .views import RideListView

urlpatterns = [
    path('', RideListView.as_view(), name='rides'),
]