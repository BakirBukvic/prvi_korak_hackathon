

# Create your views here.
from django.shortcuts import render

def ride(request):
    return render(request, 'rides.html')