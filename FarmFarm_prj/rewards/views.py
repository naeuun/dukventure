from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Reward
from django.shortcuts import render
import json

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
        'character_name': reward.character_name,
    }
    return JsonResponse(data)

@login_required
@require_POST # 이 뷰는 POST 요청만 허용합니다.
def update_character_name(request):
    """
    AJAX POST 요청을 받아 캐릭터 이름을 변경합니다.
    """
    try:
        # 요청 본문(body)에서 JSON 데이터를 읽어옵니다.
        data = json.loads(request.body)
        new_name = data.get('character_name')

        if not new_name or len(new_name) > 50:
            return JsonResponse({'status': 'error', 'message': '이름이 유효하지 않습니다.'}, status=400)

        # 현재 로그인한 사용자의 Reward 객체를 찾아 이름을 변경하고 저장합니다.
        reward = Reward.objects.get(user=request.user)
        reward.character_name = new_name
        reward.save(update_fields=['character_name'])

        return JsonResponse({'status': 'success', 'message': '캐릭터 이름이 성공적으로 변경되었습니다.'})

    except Reward.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '리워드 정보를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
