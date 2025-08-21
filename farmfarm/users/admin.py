from django.contrib import admin
from .models import User, Seller, Buyer

admin.site.register(User)
admin.site.register(Seller)
admin.site.register(Buyer)
