from django.urls import path
from .views import PenguinCollectionView, unlock_penguin, uncollected_count

app_name = 'penguins'

urlpatterns = [
    path('', PenguinCollectionView.as_view(), name='collection'),
    path('unlock/<int:penguin_id>/', unlock_penguin, name='unlock_penguin'),
     path('uncollected_count/', uncollected_count, name='uncollected_count'),  
    
]