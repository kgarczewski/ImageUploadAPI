from urllib.parse import urlparse
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.test import RequestFactory
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from django.core.files import File
from PIL import Image as pilimage
from ImageUploadAPI.serializers import ImageSerializer, ImageCreateSerializer
from ImageUploader.models import Image, CustomUser, Plan
import os


class ImageSerializerTestCase(APITestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = Site.objects.create(domain='localhost', name='localhost')
        self.plan = Plan.objects.create(
            name='premium',
            thumbnail_200=True,
            thumbnail_400=True,
            original_file=True,
            expiring_links=True,
            small_thumbnail_size=100,
            large_thumbnail_size=300,
        )
        self.user = CustomUser.objects.create(
            username='testuser',
            password='testpass',
            account_tier=self.plan,
        )
        self.image = Image.objects.create(
            user=self.user,
            image=SimpleUploadedFile("image.jpg", b"file_content", content_type="image/jpg"),
            small_thumbnail=SimpleUploadedFile("file_small.jpg", b"file_content_small", content_type="image/jpg"),
            large_thumbnail=SimpleUploadedFile("file_large.jpg", b"file_content_large", content_type="image/jpg")
        )
        self.request = self.factory.get('/', HTTP_HOST=self.site.domain)
        self.request.user = self.user

    def test_to_representation(self):
        request = self.factory.get('/')
        request.user = self.user
        serializer_context = {'request': request}
        serializer = ImageSerializer(instance=self.image, context=serializer_context)
        result = serializer.data
        self.assertIn('image', result)
        self.assertIn('small_thumbnail', result)
        self.assertIn('large_thumbnail', result)


class ImageCreateSerializerTestCase(APITestCase):
    def setUp(self):
        self.plan = Plan.objects.create(
            name='premium',
            thumbnail_200=True,
            thumbnail_400=True,
            original_file=True,
            expiring_links=True,
            small_thumbnail_size=100,
            large_thumbnail_size=300,
        )
        self.user = CustomUser.objects.create(
            username='testuser',
            password='testpass',
            account_tier=self.plan,
        )
        self.image = Image.objects.create(user=self.user, image='media/images/Figure_1.png')

    def test_create_valid_data(self):
        # create a file to upload
        rgba_image = pilimage.open('ImageUploader/tests/test_image/ball.jpg')
        rgb_image = rgba_image.convert('RGB')
        rgb_image.save('media/images/Figure_1.png')

        path = "media/images/Figure_1.png"
        request = RequestFactory().get('/')
        with open(path, "rb") as f:
            file_obj = File(f, name=os.path.basename(path))
            file_obj.seek(0)
            serializer = ImageCreateSerializer(data={"image": file_obj},
                                               context={"request": request, "user": self.user})
            self.assertTrue(serializer.is_valid(), serializer.errors)
            with transaction.atomic():
                serializer.save(user=self.user)

        actual_path = urlparse(serializer.data["image"]).path
        self.assertIsNotNone(serializer.instance.pk)
        self.assertIsNotNone(serializer.instance.image)
        self.assertIsNotNone(serializer.instance.small_thumbnail)
        self.assertIsNotNone(serializer.instance.large_thumbnail)

        self.assertEqual(serializer.data['id'], serializer.instance.pk)
        self.assertEqual(actual_path, serializer.instance.image.url)
        self.assertEqual(serializer.instance.small_thumbnail.height, self.user.account_tier.small_thumbnail_size)
        self.assertEqual(serializer.instance.large_thumbnail.height, self.user.account_tier.large_thumbnail_size)
        self.assertIn('/media/', serializer.instance.small_thumbnail.url)
        self.assertIn('/media/', serializer.instance.large_thumbnail.url)

    def test_create_invalid_data(self):
        serializer = ImageCreateSerializer(data={}, context={'request': RequestFactory().get('/'), 'user': self.user})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'image': [ErrorDetail(string='No file was submitted.', code='required')]})
