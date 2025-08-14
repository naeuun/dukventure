from django.db import models
# 'stores' 앱의 Store 모델을 가져옵니다.
from stores.models import Store
# 우선 ForeignKey 필드에서 'stores.Store' 문자열 형태로 사용하여 앱 간 순환 참조 문제를 방지합니다.

class Ingredient(models.Model):
    """
    AI가 인식하고 분류할 기본 재료 모델 (예: 계란, 콩나물, 시금치)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="재료명")
    description = models.TextField(blank=True, null=True, verbose_name="재료 설명")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "재료"
        verbose_name_plural = "재료 목록"


class Product(models.Model):
    """
    개별 가게에서 판매하는 실제 상품 모델 (예: 행복농장 유기농 계란 10구)
    """
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name="판매 가게"
    )
    # AI가 '비빔밥' -> '계란'을 추천하면, 이 필드를 통해 '계란'을 파는 Product들을 찾습니다.
    ingredient = models.ForeignKey(
        Ingredient, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='products',
        verbose_name="기본 재료"
    )
    name = models.CharField(max_length=255, verbose_name="상품명")
    price = models.PositiveIntegerField(verbose_name="가격")
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, null=True, verbose_name="상품 이미지")
    description = models.TextField(blank=True, null=True, verbose_name="상품 설명")
    is_available = models.BooleanField(default=True, verbose_name="판매중 여부")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return f'[{self.store.name}] {self.name}'

    class Meta:
        verbose_name = "판매 상품"
        verbose_name_plural = "판매 상품 목록"
        ordering = ['-created_at']