from django.contrib import admin
from .models import Reservation, ReservationItem
admin.site.register(Reservation)
admin.site.register(ReservationItem)