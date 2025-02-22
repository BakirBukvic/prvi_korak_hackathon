from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model


def calculate_penguins_saved(distance):
    # Divide distance by 83 and round to 2 decimal places
        return round(distance / 83, 2)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'user_profile.html'
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['penguins_saved'] = calculate_penguins_saved(user.km_passed)
        return context
    
    def get_object(self, queryset=None):
        return self.request.user