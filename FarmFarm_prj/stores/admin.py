from django.contrib import admin
from .models import Store, Keyword, StoreReport, StoreItem

admin.site.register(Store)
admin.site.register(Keyword)
admin.site.register(StoreReport)
admin.site.register(StoreItem)
