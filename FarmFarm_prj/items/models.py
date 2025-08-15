from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name='품목명')

    def __str__(self):
        return self.name


