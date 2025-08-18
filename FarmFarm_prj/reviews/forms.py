from django import forms
from .models import Review

# UI에 있는 키워드 목록
KEYWORD_CHOICES = [
    ('신선해요', '#신선해요'),
    ('저렴해요', '#저렴해요'),
    ('친절해요', '#친절해요'),
    ('국내산', '#국내산'),
    ('매일판매', '#매일판매'),
    ('덤이있어요', '#덤이있어요'),
    ('정직해요', '#정직해요'),
    ('한정판매', '#한정판매'),
    ('수확직송', '#수확직송'),
]

class ReviewForm(forms.ModelForm):
    # 키워드를 체크박스로 선택받기 위해 MultipleChoiceField 사용
    keywords = forms.MultipleChoiceField(
        choices=KEYWORD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="키워드 선택"
    )

    class Meta:
        model = Review
        fields = ['rating', 'photo', 'content', 'keywords']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}), # 별점 JS 라이브러리와 연동
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': '상세한 후기를 남겨주세요.'}),
        }

    def save(self, commit=True):
        review = super().save(commit=False)
        selected_keywords = self.cleaned_data.get('keywords', [])
        # 키워드가 있으면 "#키워드1#키워드2" 형태로 저장
        if selected_keywords:
            review.keywords = "".join([f"#{kw}" for kw in selected_keywords])
        else:
            review.keywords = ""
        if commit:
            review.save()
        return review

