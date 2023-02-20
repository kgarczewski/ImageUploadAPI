from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from .models import CustomUser
User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'account_tier')

    def clean_account_tier(self):
        account_tier = self.cleaned_data['account_tier']
        if not account_tier:
            raise ValidationError('Account tier is required.')
        return account_tier
