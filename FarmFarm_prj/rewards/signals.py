from django.db.models.signals import post_save
from django.dispatch import receiver
from reviews.models import Review
from stores.models import Store
from .models import Reward


# Review가 생성된 후 실행될 함수
@receiver(post_save, sender=Review)
def grant_reward_for_review(sender, instance, created, **kwargs):
    """
    새로운 리뷰가 작성되면(created=True), 작성자에게 리워드를 지급합니다.
    """
    if created:
        try:
            # [최종 수정]
            # Review -> Reservation -> Buyer -> User 순서로 접근합니다.
            user = instance.reservation.buyer.user
        except AttributeError:
            # 경로에 문제가 있을 경우, 서버 로그에 에러를 남기고 조용히 종료합니다.
            print(f"ERROR: Could not get user from review(pk={instance.pk}). Path 'instance.reservation.buyer.user' is incorrect.")
            return

        # 해당 유저의 Reward 객체를 가져오거나, 없으면 새로 생성합니다.
        reward, _ = Reward.objects.get_or_create(user=user)
        
        # 스탬프를 추가합니다.
        reward.add_stamp()
        print(f"INFO: Stamp successfully added for user '{user.username}' for new review.")


# Store가 생성된 후 실행될 함수
@receiver(post_save, sender=Store)
def grant_reward_for_store_registration(sender, instance, created, **kwargs):
    """
    새로운 가게가 등록되면(created=True), 가게 주인에게 리워드를 지급합니다.
    """
    if created:
        try:
            # Store 모델의 owner 필드가 User 객체를 직접 가리킨다고 가정합니다.
            # 만약 Seller 모델을 거쳐야 한다면 'instance.owner.user' 등으로 수정해야 합니다.
            user = instance.owner
        except AttributeError:
            print(f"ERROR: Could not get user from store(pk={instance.pk}). Path 'instance.owner' is incorrect.")
            return

        reward, _ = Reward.objects.get_or_create(user=user)
        reward.add_stamp()
        print(f"INFO: Stamp successfully added for user '{user.username}' for new store registration.")
