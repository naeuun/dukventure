from django.db import models

# Create your models here.

class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

