from .models import Plan, Image, CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, UserChangeForm, UserCreationForm
from .models import CustomUser
from .forms import CustomUserCreationForm
from django import forms


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm




# Register your models here.
admin.site.register(Plan)
admin.site.register(Image)
admin.site.register(CustomUser, CustomUserAdmin)
