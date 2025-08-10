from django.db import models

class ReviewKeyword(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __str__(self): return self.name

class Review(models.Model):
    reservation = models.OneToOneField('reservations.Reservation', on_delete=models.CASCADE, related_name='review')
    store = models.ForeignKey('users.Store', on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey('users.Buyer', on_delete=models.CASCADE, related_name='reviews')

    rating = models.PositiveSmallIntegerField()  # 1~5 (뷰에서 검증)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                                   name='review_rating_1_5'),
        ]
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f'{self.store.name} - {self.author.user.username} ({self.rating})'

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/%Y/%m/%d/')
    def __str__(self): return f'Image for Review {self.review_id}'

class ReviewKeywordMap(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='keyword_maps')
    keyword = models.ForeignKey(ReviewKeyword, on_delete=models.CASCADE, related_name='keyword_maps')

    class Meta:
        unique_together = (('review', 'keyword'),)
