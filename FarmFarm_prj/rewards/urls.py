from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
        # ex: /rewards/my-page/
    path('my-page/', views.reward_page, name='reward_page'),
    
    # API 엔드포인트 (기존과 동일)
    # ex: /rewards/status/
    path('status/', views.get_reward_status, name='get_reward_status'),
    path('update-name/', views.update_character_name, name='update_character_name'),
]