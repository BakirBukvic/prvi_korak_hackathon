from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from base.models import PenguinCollected

class PenguinCollectionView(LoginRequiredMixin, ListView):
    model = PenguinCollected
    template_name = 'penguins.html'
    context_object_name = 'penguins'

    def get_queryset(self):
        return PenguinCollected.objects.filter(
            user=self.request.user
        ).select_related('penguin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_penguins'] = self.request.user.penguins_saved
        context['unlocked_penguins'] = self.get_queryset().filter(is_collected=True).count()
        return context

@login_required
@require_POST
def unlock_penguin(request, penguin_id):
    try:
        penguin_collected = PenguinCollected.objects.get(
            id=penguin_id,
            user=request.user,
            is_collected=False
        )
        penguin_collected.is_collected = True
        penguin_collected.save()
        return JsonResponse({
            'success': True,
            'name': penguin_collected.penguin.penguin_name
        })
    except PenguinCollected.DoesNotExist:
        return JsonResponse({'success': False}, status=404)