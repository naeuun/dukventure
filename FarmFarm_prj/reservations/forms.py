from django import forms
from .models import Reservation, ReservationItem, RejectReason, ReservationStatus
from django.utils import timezone

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['store', 'requested_pickup_at', 'note', 'contact_phone']
        widgets = {
            'requested_pickup_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_requested_pickup_at(self):
        # 시간 유효성 검사 로직
        pickup_time = self.cleaned_data.get('requested_pickup_at')
        if pickup_time and pickup_time < timezone.now():
            raise forms.ValidationError("과거 시간으로는 예약할 수 없습니다.")
        return pickup_time

class ReservationItemForm(forms.ModelForm):
    class Meta:
        model = ReservationItem
        fields = ['item_name', 'unit_price', 'quantity', 'unit']

# 판매자의 예약 거절/상태 변경을 위한 폼
class SellerReservationUpdateForm(forms.ModelForm):
    # 거절 사유를 모델의 choices에서 가져와 radio 버튼으로 렌더링
    rejected_reason = forms.ChoiceField(
        choices=RejectReason.choices, 
        widget=forms.RadioSelect, 
        required=False
    )

    class Meta:
        model = Reservation
        fields = ['rejected_reason']
