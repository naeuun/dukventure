from django.contrib import admin
from .models import Review, ReviewImage, ReviewKeyword, ReviewKeywordMap
admin.site.register(Review)
admin.site.register(ReviewImage)
admin.site.register(ReviewKeyword)
admin.site.register(ReviewKeywordMap)