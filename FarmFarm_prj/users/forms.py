from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'usertype', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "사용자 이름"
        self.fields['usertype'].label = "사용자 유형"
        self.fields['password1'].label = "비밀번호"
        self.fields['password2'].label = "비밀번호 확인"