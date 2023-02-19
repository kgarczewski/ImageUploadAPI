from datetime import timedelta
from django.core.signing import TimestampSigner
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APITestCase
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory, force_authenticate
from ImageUploader.models import Image, CustomUser, Plan
from ImageUploadAPI.views import ImageView
from PIL import Image as pilimage
import os
from django.core.files import File
from django.utils import timezone


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
        response.render()  # Render the response content before accessing it
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
        user = self.user
        force_authenticate(request, user=user)
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
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass',
        )
        self.account_tier = Plan.objects.create(
            name='Test Tier', small_thumbnail_size=100, large_thumbnail_size=200
        )
        self.user.account_tier = self.account_tier
        self.user.save()

    def test_create_image(self):
        self.client.force_login(self.user)  # log in the user
        # create a file to upload
        rgba_image = pilimage.open('/home/krzysztof/Desktop/ImageUploadAPI/media/images/Figure_1.png')
        rgb_image = rgba_image.convert('RGB')
        rgb_image.save('/home/krzysztof/Desktop/ImageUploadAPI/media/images/Figure_1.png')

        path = "/home/krzysztof/Desktop/ImageUploadAPI/media/images/Figure_1.png"
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
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass',
        )
        self.account_tier = Plan.objects.create(
            name='Test Tier', small_thumbnail_size=100, large_thumbnail_size=200
        )
        self.user.account_tier = self.account_tier
        self.user.save()
        self.image = Image.objects.create(user=self.user)

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
