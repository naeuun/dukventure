from django.contrib import admin
from .models import Reward

# Reward 모델을 관리자 페이지에서 볼 수 있도록 등록합니다.
@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    # 관리자 페이지 목록에 보일 필드들을 지정합니다.
    list_display = ('user', 'stamp_count', 'medal_tier', 'character_level')
    # 사용자 이름으로 검색할 수 있는 검색창을 추가합니다.
    search_fields = ('user__username',)
