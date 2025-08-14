from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name='품목명')
    description = models.TextField(blank=True, null=True, verbose_name='설명')

    def __str__(self):
        return self.name


