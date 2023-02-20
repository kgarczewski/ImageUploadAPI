from datetime import timedelta
from django.core.files.base import ContentFile
from django.core.signing import TimestampSigner
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.test import RequestFactory
from ImageUploader.models import Image, CustomUser, Plan
from ImageUploadAPI.views import ImageView
from PIL import Image as pilimage
import os
from django.core.files import File
from django.utils import timezone
import time


class TestImageView(APITestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.factory = APIRequestFactory()
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
        self.image1 = Image.objects.create(user=self.user, image="image1.png", small_thumbnail="thumb1.png",
                                           large_thumbnail="thumb2.png", expiration_link="link1.com")
        self.image2 = Image.objects.create(user=self.user, image="image2.png", small_thumbnail="thumb3.png",
                                           large_thumbnail="thumb4.png", expiration_link="link2.com")

        self.view = ImageView.as_view({'get': 'list'})

    def test_image_view_list(self):
        request = self.factory.get('/')
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'image1.png')
        self.assertContains(response, 'image2.png')
        self.assertContains(response, 'thumb1.png')
        self.assertContains(response, 'thumb2.png')
        self.assertContains(response, 'thumb3.png')
        self.assertContains(response, 'thumb4.png')
        self.assertContains(response, 'link1.com')
        self.assertContains(response, 'link2.com')

    def test_image_view_list_no_request(self):
        request = RequestFactory().get('')
        request.user = self.user
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data['images'][0]['image'], 'image1.png')
        self.assertEqual(response.data['images'][0]['small_thumbnail'], 'thumb1.png')
        self.assertEqual(response.data['images'][0]['large_thumbnail'], 'thumb2.png')
        self.assertEqual(response.data['images'][0]['expiration_link'], 'link1.com')
        self.assertEqual(response.data['images'][1]['image'], 'image2.png')
        self.assertEqual(response.data['images'][1]['small_thumbnail'], 'thumb3.png')
        self.assertEqual(response.data['images'][1]['large_thumbnail'], 'thumb4.png')
        self.assertEqual(response.data['images'][1]['expiration_link'], 'link2.com')


class TestImageCreateView(APITestCase):
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

    def test_create_image(self):
        self.client.force_login(self.user)  # log in the user
        # create a file to upload
        rgba_image = pilimage.open('ImageUploader/tests/test_image/ball.jpg')
        rgb_image = rgba_image.convert('RGB')
        rgb_image.save('ImageUploader/tests/test_image/ball.jpg')

        path = "ImageUploader/tests/test_image/ball.jpg"
        with open(path, "rb") as f:
            file_obj = File(f, name=os.path.basename(path))
            file_obj.seek(0)  # rewind the file pointer
            data = {
                'image': file_obj,
                'small_thumbnail': 'thumbnail.png',
                'large_thumbnail': 'thumbnail.png',
                'expiration_link': 'link.com',
            }
            response = self.client.post(reverse('addimage-list'), data=data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Image.objects.count(), 1)


class GenerateExpiringUrlViewTest(APITestCase):
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

    def test_generate_expiring_url(self):
        self.client.force_login(self.user)
        expiration_seconds = 3600
        url = reverse('expiration_link', args=[self.image.pk])
        data = {'expiration_seconds': expiration_seconds}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['expired'], False)
        self.assertIn('url', response.data)
        # self.assertIn(self.image.get_absolute_url(), response.data['url'])

        # Check that the expiration token was set on the image.
        self.image.refresh_from_db()
        signer = TimestampSigner()
        expected_expiration_time = timezone.now() + timedelta(seconds=expiration_seconds)
        expected_expiration_token = signer.sign(str(expiration_seconds))
        self.assertEqual(
            self.image.expiration_date.replace(microsecond=0), expected_expiration_time.replace(microsecond=0)
        )
        self.assertEqual(self.image.expiration_token, expected_expiration_token)
        self.assertEqual(self.image.expiration_link, response.data['url'])


class ExpirationLinkViewTestCase(APITestCase):
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
        self.image = Image.objects.create(user=self.user, image="image.jpg", expiration_token="token123")

    def test_post_request_with_expiration_seconds(self):
        expiration_link = reverse('expiration_link', kwargs={'image_id': self.image.id})
        data = {'expiration_seconds': 500}
        response = self.client.post(expiration_link, data)
        self.assertEqual(response.status_code, 200)

    def test_post_request_without_expiration_seconds(self):
        url = reverse('expiration_link', kwargs={'image_id': self.image.id})
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse('expiration_seconds' in response.data)


class ServeImageViewTestCase(APITestCase):
    def generate_signature(self, image_id):
        signer = TimestampSigner()
        value = '{}{}'.format(image_id, int(time.time()))
        return signer.sign(value)

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
        self.image = Image.objects.create(
            user=self.user,
            image='images/test.jpg',
            small_thumbnail='images/test_small_thumbnail.jpg',
            large_thumbnail='images/test_large_thumbnail.jpg',
        )
        self.signer = TimestampSigner()

    def test_serve_expired_image(self):
        # Set an expiration date in the past.
        image = Image.objects.create(
            user=self.user,
            image=ContentFile(b'Test image content', 'test_image.png'),
            expiration_date=timezone.now() - timezone.timedelta(hours=1),
        )

        # Save the image file before generating the signature
        image.image.save(image.image.name, ContentFile(b'Test image content', 'test_image.png'))
        image.save()

        # Generate the signature
        signature = self.generate_signature(image.id)

        # Try to access the expired image using the signature
        response = self.client.get(reverse('serve-image', args=[image.id, signature]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
