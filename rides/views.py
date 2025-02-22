from django.shortcuts import render, redirect
from django.views.generic import ListView
from base.models import Ride, RouteDetails
from django.views.generic import CreateView

from django.views.generic import ListView
from django.views.generic import CreateView
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import re
from django.urls import reverse

class RideListView(ListView):
    model = Ride
    template_name = 'rides.html'
    context_object_name = 'rides'

    def get_queryset(self):
        # Use select_related instead of prefetch_related since it's a OneToOne relationship
        return Ride.objects.select_related('route_details').all().order_by('-created_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add debug information to help track data
        context['origin_latitude'] = 44.7066641
        context['origin_longitude'] = 18.3107132
        context['destination_latitude'] = 43.34377480000001
        context['destination_longitude'] = 17.8077578
        context['selected_route_polyline'] = "qwzoGaiwnBd}@dbAhQdn@_Kpj@?n_A}g@d`Bqk@v}Aef@rw@}b@x{CoVz~C_E`fAzQd}AQ`pC_RjlBig@xy@fH`~@dfAtS`_BhwAh`Apu@dtAa@zd@fMRhIbq@lNjt@y`AlmA}`@d@kn@rWaH`w@xP~{@ws@nm@yGlh@zYvOrb@bt@gNpuAim@d_@xMbd@gk@tkAxp@ng@m@`yAv`@xi@`U`Oek@tb@mHnx@lnAfnAlJn`Aw_@tu@|~AlrAnKf}@zSf}Ar}@fn@z{Afy@rq@rQxzB|a@dtAz[|Inp@_u@|a@rGhUjjAhr@fi@duAstA`m@}_@b{@|n@d}@j~Act@h{CjLjlC~a@zq@rrAnPdv@p{@~`Avp@zj@q@|TuXds@zJrj@jjAxa@~n@|t@l]~hB|JxQebBla@a[lcAxMhaCe{AtYcAzMpYtMcMdi@n_@nZrr@za@rlAmDpl@rRrh@zNvk@}M|i@vOzUzXmCtKpPBmE`Kb[bBbe@zSoPvH~QbKvZzt@h\tRtlA|[bM~b@fr@_`@vgAs|@hn@m]hwAaYnxBm`AnaAi|@|xA{]la@yk@v`ArX`Ynd@j\pNneAv]fqBrb@`g@dg@pDj`AhBpr@sD~l@i@~u@|Tj^dg@beAnLrd@|Tjg@?jf@~^ri@aDneA|@`|@jCzYei@fGnKvMcKbD_j@dWlKlZwLjMnZbG~\j]~Hlu@ycAzWuPzVta@rl@yHd]eQ`UbKnO~RdYhw@rKhgAtQ|_Al[`}@hlArRja@`R`Wvj@tuAvq@pXfMbRnZ~x@hc@hp@rG`MxC~Y}S`o@ktAvf@u[xp@vJvXfCbSo]jn@~[zeAzs@zuA|PrdAu`@zaAz]peAwNdd@xXuDdr@^ieAbIix@vg@y_BbCu]rTF~Nbl@l_@|IvLzBbOmXl{@evAdVvHtMySnF`K`DpTvSlYhDaa@kN}AxSwi@vOcjAth@ybAdeA_rAb_@yXpQjGv`AgAtu@kBna@]d]o[hRmb@fK~GbCg|@|YibAxa@qd@jWt@vQuIhMqZvV[zVu@Auj@zC{Zr\{@|a@tHzf@rZxsAsrB}Gkc@l_@mYnHco@fXoP~b@tn@zb@I`d@_`@f_@d\zTeDf`@xQpp@zr@xT|\`l@B`f@jJxYxWdcAtyAzsAzCdx@oL`z@tGx|@ap@d{CikAty@ik@ne@ohAfYuuAv{@iu@tXk_Bz`AssBtbC{oApk@{w@lSsy@`|@wnAh_BqqAjYsSdqBlYlvBbyBhdA`wAh[x~Bt`@ba@ty@Db[dMh@vO00"

        for ride in context['rides']:
            print(f"Ride {ride.id}: Has route_details: {hasattr(ride, 'route_details')}")
        return context

class MakeRideView(CreateView):
    model = Ride
    template_name = 'make_ride.html'
    fields = ['start_date', 'distance', 'duration', 'travelers']


def create_ride_from_post_data(post_data):
    # Parse duration string (e.g. "2 hours 30 mins" to timedelta)
    duration_str = post_data.get('duration_text', '')
    duration = parse_duration_string(duration_str)

    # Create a new ride object
    ride = Ride(
        start=post_data.get('origin'),
        end=post_data.get('destination'), 
        distance=post_data.get('distance_km'),
        duration=duration,
        travelers=post_data.get('travelers'),
        created_on=timezone.now(),
        start_date=timezone.now(),
        arriving_date=timezone.now()
    )
    ride.save()
    return ride

def create_ride_details_from_post_data(post_data, ride):
    """
    Creates a RouteDetails instance from POST data and associates it with a ride
    Args:
        post_data: The POST request data
        ride: The Ride instance to associate with
    Returns:
        RouteDetails instance
    """
    route_details = RouteDetails(
        ride=ride,
        origin_place_id=post_data.get('origin_place_id'),
        origin_latitude=float(post_data.get('origin_latitude')),
        origin_longitude=float(post_data.get('origin_longitude')),
        destination_place_id=post_data.get('destination_place_id'),
        destination_latitude=float(post_data.get('destination_latitude')),
        destination_longitude=float(post_data.get('destination_longitude')),
        distance_km=float(post_data.get('distance_km')),
        duration_text=post_data.get('duration_text'),
        selected_route_index=int(post_data.get('selected_route_index')),
        selected_route_polyline=post_data.get('selected_route_polyline')
    )
    route_details.save()
    return route_details



def parse_duration_string(duration_str):
    # Extract hours and minutes from strings like "2 hours 30 mins"
    hours = 0
    minutes = 0
    
    hour_match = re.search(r'(\d+)\s*hour', duration_str)
    if hour_match:
        hours = int(hour_match.group(1))
        
    min_match = re.search(r'(\d+)\s*min', duration_str)
    if min_match:
        minutes = int(min_match.group(1))
        
    return timedelta(hours=hours, minutes=minutes)




def submitRide(request):
    if request.method == 'POST':
        try:
            # Create the ride first
            ride = create_ride_from_post_data(request.POST)
            # Create the route details and associate with the ride
            route_details = create_ride_details_from_post_data(request.POST, ride)
            return redirect(reverse('rides'))
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    