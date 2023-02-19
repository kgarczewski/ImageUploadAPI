from rest_framework import serializers
from ImageUploader.models import Image
from PIL import Image as PILImage
from django.contrib.sites.shortcuts import get_current_site
from .utils import (
    create_large_thumbnail,
    create_small_thumbnail,
)


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['image', 'small_thumbnail', 'large_thumbnail']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        site = get_current_site(request)
        if instance.small_thumbnail:
            data['small_thumbnail'] = "http://{}{}".format(site.domain, instance.small_thumbnail.url)
        if instance.large_thumbnail:
            data['large_thumbnail'] = "http://{}{}".format(site.domain, instance.large_thumbnail.url)
        if not request.user.account_tier.original_file:
            data.pop('image')
        if not request.user.account_tier.thumbnail_400:
            data.pop('large_thumbnail')
        return data


class ImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']
        extra_kwargs = {"input_field": {"write_only": True}}

    def get_small_thumbnail(self, obj):
        return self.context['request'].build_absolute_uri(obj.small_thumbnail.url)

    def get_large_thumbnail(self, obj):
        return self.context['request'].build_absolute_uri(obj.large_thumbnail.url)

    def create(self, validated_data):
        user = validated_data.get('user')
        image = validated_data.get('image')
        image = PILImage.open(image)
        image = image.convert("RGB")

        validated_data['small_thumbnail'] = create_small_thumbnail(image, user.account_tier.small_thumbnail_size)
        validated_data['large_thumbnail'] = create_large_thumbnail(image, user.account_tier.large_thumbnail_size)

        return super().create(validated_data)


