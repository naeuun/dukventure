from django.db import models

class Item(models.Model):
<<<<<<< HEAD
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, help_text='단위(봉, 단, kg 등)') #추가
=======
    name = models.CharField(max_length=100, verbose_name='품목명')
    description = models.TextField(blank=True, null=True, verbose_name='설명')
>>>>>>> backend

    def __str__(self):
        return self.name


