from django import forms
from .models import Store, StoreItem, StoreReport

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'address', 'sale_days', 'sale_hours', 'payment_methods', 'contact', 'photo', 'description']
        labels = {
            'name': '가게 이름',
            'price_info': '가격 정보',
            'sale_days': '판매 요일',
            'sale_hours': '판매 시간대',
            'payment_methods': '결제 수단',
            'contact': '연락처',
            'description': '특이 사항/판매 메시지',
        }

class StoreItemForm(forms.ModelForm):
    class Meta:
        model = StoreItem
        fields = ['item', 'price', 'photo', 'description', 'unit']
        labels = {
            'item': '품목명',
            'price': '가격',
            'photo': '사진',
            'description': '설명',
            'unit': '단위'
        }
        
class StoreReportForm(forms.ModelForm):
    class Meta:
        model = StoreReport
        fields = ['image', 'report_items','address', 'time', 'keywords']
        labels = {
            'image': '이미지',
            'address': '주소',
            'time' :'시간',
            'keywords': '키워드',
            'report_items': '품목'
        }