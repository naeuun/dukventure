from django.db import models

class PlanStatus(models.TextChoices):
    DRAFT            = 'DRAFT', '작성중'
    SUGGESTED        = 'SUGGESTED', '추천완료'
    PARTIAL_RESERVED = 'PARTIAL_RESERVED', '일부예약'
    RESERVED         = 'RESERVED', '전체예약완료'
    DONE             = 'DONE', '완료'

class ShoppingPlan(models.Model):
    buyer = models.ForeignKey('users.Buyer', on_delete=models.CASCADE, related_name='shopping_plans')
    dish_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=PlanStatus.choices, default=PlanStatus.DRAFT)

    # (선택) AI 메타
    ai_model = models.CharField(max_length=50, blank=True)
    ai_prompt = models.TextField(blank=True)
    ai_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.dish_name} - {self.buyer.user.username}'

class ShoppingPlanItem(models.Model):
    plan = models.ForeignKey(ShoppingPlan, on_delete=models.CASCADE, related_name='items')

    ingredient_name = models.CharField(max_length=100)
    quantity = models.FloatField(default=1.0)
    unit = models.CharField(max_length=20, blank=True)
    expected_unit_price = models.PositiveIntegerField(default=0)
    expected_store_name = models.CharField(max_length=100, blank=True)

    # 추천/선택된 상점 및 실제 예약 연결(선택)
    suggested_store = models.ForeignKey('users.Store', null=True, blank=True, on_delete=models.SET_NULL, related_name='suggested_plan_items')
    reservation = models.ForeignKey('reservations.Reservation', null=True, blank=True, on_delete=models.SET_NULL, related_name='plan_items')
    reservation_item = models.ForeignKey('reservations.ReservationItem', null=True, blank=True, on_delete=models.SET_NULL, related_name='plan_items')

    is_reserved = models.BooleanField(default=False)
    order_index = models.PositiveSmallIntegerField(default=0)
    memo = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['order_index', 'id']

    def __str__(self):
        return f'{self.ingredient_name} ({self.quantity}{self.unit})'
