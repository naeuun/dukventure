from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'usertype', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "사용자 이름"
        self.fields['usertype'].label = "사용자 유형"
        self.fields['phone'].label = "전화번호"
        self.fields['password1'].label = "비밀번호"
        self.fields['password2'].label = "비밀번호 확인"

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'profile_image', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "사용자 이름"
        self.fields['profile_image'].label = "프로필 이미지"
        self.fields['phone'].label = "전화번호"