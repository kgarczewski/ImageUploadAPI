from .models import Plan, Image, CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, UserChangeForm, UserCreationForm
from .models import CustomUser
from .forms import CustomUserCreationForm
from django import forms


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'account_tier'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Tier info', {'fields': ('account_tier',)}),
    )
    list_display = ['email', 'username', 'account_tier']



# Register your models here.
admin.site.register(Plan)
admin.site.register(Image)
admin.site.register(CustomUser, CustomUserAdmin)
