from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. We will not share your email.')


class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')


def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError('A user with that email already exists.')
    return email
        

