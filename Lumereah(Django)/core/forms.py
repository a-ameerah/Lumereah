from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm


from .models import UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "signup-input",
                "placeholder": "Enter your email",
            }
        ),
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "signup-input",
                "placeholder": "Enter your name",
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "signup-input",
                "placeholder": "Enter your password",
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "signup-input",
                "placeholder": "Confirm your password",
            }
        )
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")




class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "signup-input",
                "placeholder": "Enter your name",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "signup-input",
                "placeholder": "Enter your password",
            }
        )
    )

