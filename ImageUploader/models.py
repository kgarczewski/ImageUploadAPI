from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    thumbnail_200 = models.BooleanField(null=True)
    thumbnail_400 = models.BooleanField(null=True)
    original_file = models.BooleanField(null=True)
    expiring_links = models.BooleanField(null=True)
    small_thumbnail_size = models.IntegerField(default=200)
    large_thumbnail_size = models.IntegerField(default=400)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    account_tier = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name='account_tier_users', to_field='name', null=True
    )


class Image(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='images')
    small_thumbnail = models.ImageField(upload_to='small_thumbnail', blank=True, null=True)
    large_thumbnail = models.ImageField(upload_to='large_thumbnail', blank=True, null=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    expiration_token = models.CharField(max_length=255, null=True, blank=True)
    expiration_link = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f'Image {self.id}'

    def get_absolute_url(self):
        return reverse('serve-image', kwargs={'image_id': self.pk})
