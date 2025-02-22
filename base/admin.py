from django.contrib import admin
from base.models import User, UserLevel, Ride, UserRideAssociation, RideApplication


admin.site.register(User)
admin.site.register(UserLevel)
admin.site.register(Ride)
admin.site.register(UserRideAssociation)
admin.site.register(RideApplication)