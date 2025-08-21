from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Reward
from django.shortcuts import render

@login_required
def reward_page(request):
    """
    사용자의 리워드 현황을 보여주는 전용 페이지를 렌더링합니다.
    """
    # 이 뷰는 단순히 템플릿 파일만 렌더링하고,
    # 실제 데이터는 페이지 내의 JavaScript가 API를 통해 가져옵니다.
    return render(request, 'rewards/reward_page.html')

@login_required
def get_reward_status(request):
    """
    로그인한 사용자의 현재 리워드 상태를 JSON 형태로 반환합니다.
    """
    # 현재 로그인한 사용자의 Reward 객체를 가져오거나 없으면 생성합니다.
    reward, created = Reward.objects.get_or_create(user=request.user)

    data = {
        'stamp_count': reward.stamp_count,
        'medal_tier': reward.medal_tier,
        'character_level': reward.character_level,
    }
    return JsonResponse(data)

