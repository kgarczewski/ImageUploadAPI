from django.contrib import admin
from .models import Plan, Image, CustomUser

# Register your models here.
admin.site.register(Plan)
admin.site.register(Image)
admin.site.register(CustomUser)