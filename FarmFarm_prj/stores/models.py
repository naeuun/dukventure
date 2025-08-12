from django.db import models

class Store(models.Model):  # 판매자가 등록하는 가게 모델
    seller = models.ForeignKey('users.Seller', on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    business_number = models.CharField(max_length=20, blank=True, null=True)  # 사업자 등록 번호
    items = models.ManyToManyField('items.Item', related_name='stores', blank=True)  # 판매자가 등록한 물품
    price_info = models.CharField(max_length=100, blank=True, null=True)  # 가격 정보(선택사항)
    sale_days = models.CharField(max_length=50, blank=True, null=True)  # 판매 요일 (예: 월~금)
    sale_hours = models.CharField(max_length=50, blank=True, null=True)  # 판매 시간대 (예: 09:00~18:00)
    payment_methods = models.CharField(max_length=100, blank=True, null=True)  # 결제 수단
    contact = models.CharField(max_length=50, blank=True, null=True)  # 판매자 연락 수단(선택사항)
    photo = models.ImageField(upload_to='store_photos/', blank=True, null=True)  # 가게 사진 업로드(선택사항)
    description = models.TextField(blank=True, null=True)  # 특이 사항 또는 판매 메시지

    def __str__(self):
        return f'Store: {self.name} ({self.seller.user.username})'


class Keyword(models.Model):
    keyword = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.keyword


class StoreReport(models.Model):
    reporter = models.ForeignKey('users.Buyer', on_delete=models.CASCADE, related_name='reports')
    store_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to='store_reports/', blank=True, null=True)
    food_type = models.CharField(max_length=100, blank=True, null=True)
    time = models.CharField(max_length=50, blank=True, null=True)
    keywords = models.ManyToManyField(Keyword, related_name='reports', blank=True)  # 키워드 모델 연결
    description = models.TextField(blank=True, null=True)
    items = models.ManyToManyField('items.Item', related_name='reports', blank=True)

    def __str__(self):
        return f'Report by {self.reporter.user.username} on {self.store_name}'