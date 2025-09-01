from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    

    class Meta:
        model = User
        fields=('username','email','password1','password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

            UserProfile.objects.create(
                user=user,
                
               
            )
        return user
    

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('age', 'skin_type', 'skin_concern', 'budget')
    

