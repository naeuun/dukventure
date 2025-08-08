from django.db import models
from django.contrib.auth.models import AbstractUser

class UserType(models.TextChoices):
    BUYER = 'BUYER', '구매자'
    SELLER = 'SELLER', '판매자'
    
class User(AbstractUser):
    username = models.CharField(max_length=10, unique=True)
    usertype = models.CharField(max_length=10, choices=UserType.choices)
    
    def __str__(self):
        return f'[{self.usertype}] {self.username}'
    