from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import CustomUser, Plan
User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    account_tier = forms.ModelChoiceField(
        queryset=Plan.objects.all(),
        required=True,
        empty_label=None,
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'account_tier')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.account_tier = self.cleaned_data['account_tier']
        if commit:
            user.set_password(self.cleaned_data['password1']) # hash the password
            user.save()
        return user