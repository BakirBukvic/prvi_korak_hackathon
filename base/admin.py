from django.contrib import admin
from base.models import User, UserLevel, Ride, RouteDetails


admin.site.register(User)
admin.site.register(UserLevel)
admin.site.register(Ride)
admin.site.register(RouteDetails)