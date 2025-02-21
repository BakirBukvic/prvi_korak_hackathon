from django.shortcuts import render

def userProfile(request):
    return render(request, 'user_profile.html')