from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    # OneToOneField: 예약 1개에 리뷰 1개를 보장합니다.
    reservation = models.OneToOneField(
        'reservations.Reservation', 
        on_delete=models.CASCADE,
        related_name='review'
    )
    # 작성자(구매자)와 가게 정보를 쉽게 참조하기 위해 FK로 저장합니다.
    author = models.ForeignKey(
        'users.Buyer', 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )

    # 별점 (1~5점)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    # 사진 (선택 사항)
    photo = models.ImageField(
        upload_to='reviews/%Y/%m/%d/', 
        blank=True, 
        null=True
    )
    # 키워드 리뷰 (UI에 맞춰 여러 개 선택 가능하도록)
    # 예: "#신선해요,#친절해요" 형태로 저장
    keywords = models.CharField(max_length=255, blank=True)
    # 일반 텍스트 리뷰
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f'{self.author}님의 {self.store} 리뷰'

    def get_keywords_as_list(self):
        """저장된 키워드 문자열을 리스트로 변환합니다."""
        if not self.keywords:
            return []
        # '#'를 기준으로 나누고, 빈 문자열은 제거합니다.
        return [tag.strip() for tag in self.keywords.split('#') if tag.strip()]
