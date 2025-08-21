from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from stores.models import Store

class UserType(models.TextChoices):
    BUYER = 'BUYER', '구매자'
    SELLER = 'SELLER', '판매자'
    
class User(AbstractUser):
    username = models.CharField(max_length=10, unique=True)
    usertype = models.CharField(max_length=10, choices=UserType.choices)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)  # 전화번호 필드 추가

    def __str__(self):
        return f'{self.usertype} - {self.username}'
    
class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller')
    is_registered = models.BooleanField(default=False)  # 사업자 등록 여부
    has_store = models.BooleanField(default=False)      # 가게 등록 여부
    business_number = models.CharField(max_length=10, blank=True, null=True) # 사업자등록 번호 

    def __str__(self):
        return f'Seller: {self.user.username}'
    
class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer')
    
    def __str__(self):
        return f'Buyer: {self.user.username}'

@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        if instance.usertype == UserType.BUYER:
            Buyer.objects.create(user=instance)
        elif instance.usertype == UserType.SELLER:
            Seller.objects.create(user=instance)