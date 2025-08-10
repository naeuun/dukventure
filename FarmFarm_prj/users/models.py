from django.db import models
from django.contrib.auth.models import AbstractUser

class UserType(models.TextChoices):
    BUYER = 'BUYER', '구매자'
    SELLER = 'SELLER', '판매자'

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)  # Django 기본은 150
    usertype = models.CharField(max_length=10, choices=UserType.choices, blank=True)

    def __str__(self):
        return f'{self.usertype or "USER"} - {self.username}'

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller')
    is_registered = models.BooleanField(default=False)

    def __str__(self):
        return f'Seller: {self.user.username}'

class Store(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'Store: {self.name} ({self.seller.user.username})'

class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer')

    def __str__(self):
        return f'Buyer: {self.user.username}'
