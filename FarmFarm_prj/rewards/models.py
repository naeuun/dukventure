from django.db import models
from django.conf import settings

# 사용자의 리워드 정보를 담는 모델
class Reward(models.Model):
    # 메달 등급 선택지
    class MedalTier(models.TextChoices):
        NONE = 'NONE', '없음'
        BRONZE = 'BRONZE', '동메달'
        SILVER = 'SILVER', '은메달'
        GOLD = 'GOLD', '금메달'

    # User 모델과 1:1 관계 설정. 사용자가 삭제되면 리워드 정보도 삭제됩니다.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='reward'
    )

    # 현재 스탬프 개수 (0-3개)
    stamp_count = models.IntegerField(default=0)

    # 현재 메달 등급
    medal_tier = models.CharField(
        max_length=10,
        choices=MedalTier.choices,
        default=MedalTier.NONE
    )

    # 캐릭터 성장 레벨 (1-3단계)
    character_level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}님의 리워드"

    # 스탬프를 추가하고, 4개가 모이면 레벨업하는 메서드
    def add_stamp(self):
        """
        스탬프를 1개 추가합니다.
        만약 스탬프가 4개가 되면, 스탬프를 0으로 리셋하고 메달과 캐릭터를 성장시킵니다.
        """
        if self.stamp_count < 3:
            self.stamp_count += 1
        else:
            self.stamp_count = 0
            self._level_up()
        
        self.save()

    # 메달과 캐릭터를 성장시키는 내부 메서드
    def _level_up(self):
        """
        메달 등급을 업그레이드하고 캐릭터 레벨을 올립니다.
        """
        # 메달 업그레이드 로직
        if self.medal_tier == self.MedalTier.NONE:
            self.medal_tier = self.MedalTier.BRONZE
        elif self.medal_tier == self.MedalTier.BRONZE:
            self.medal_tier = self.MedalTier.SILVER
        elif self.medal_tier == self.MedalTier.SILVER:
            self.medal_tier = self.MedalTier.GOLD
        # 금메달 이상은 변화 없음

        # 캐릭터 레벨업 로직 (최대 3레벨)
        if self.character_level < 3:
            self.character_level += 1
        
