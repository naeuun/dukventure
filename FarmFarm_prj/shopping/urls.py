from django.urls import path
from .views import AiShoppingView

app_name = 'shopping'  # 템플릿에서 {% url 'shopping:ai_shopping' %} 처럼 사용하기 위해 네임스페이스를 지정합니다.

urlpatterns = [
    # /shopping/ai/ 경로로 접속하면 AiShoppingView를 실행합니다.
    path('ai/', AiShoppingView.as_view(), name='ai_shopping'),
]