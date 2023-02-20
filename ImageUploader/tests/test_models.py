import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from ImageUploader.models import Plan, CustomUser, Image


@pytest.fixture
def plan(db):
    plan = Plan.objects.create(
        name='premium',
        thumbnail_200=True,
        thumbnail_400=True,
        original_file=True,
        expiring_links=True,
        small_thumbnail_size=100,
        large_thumbnail_size=300,
    )
    return plan


@pytest.fixture
def user(plan):
    user = CustomUser.objects.create(
        username='testuser',
        password='testpass',
        account_tier=plan,
    )
    return user


@pytest.fixture
def image(user):
    with open('ImageUploader/tests/test_image/ball.jpg', 'rb') as f:
        image_file = SimpleUploadedFile('test_image.jpg', f.read(), content_type='image/jpeg')
        return Image.objects.create(
            user=user,
            image=image_file,
        )


def test_plan_creation(plan):
    assert Plan.objects.count() == 4
    assert Plan.objects.get(id=4).name == 'premium'
    assert Plan.objects.get(id=4).thumbnail_200 is True
    assert Plan.objects.get(id=4).thumbnail_400 is True
    assert Plan.objects.get(id=4).original_file is True
    assert Plan.objects.get(id=4).expiring_links is True
    assert Plan.objects.get(id=4).small_thumbnail_size == 100
    assert Plan.objects.get(id=4).large_thumbnail_size == 300


def test_user_creation(user):
    assert CustomUser.objects.count() == 1
    assert CustomUser.objects.first().username == 'testuser'
    assert CustomUser.objects.first().password == 'testpass'


def test_image_creation(image, user):
    assert Image.objects.count() == 1
    assert Image.objects.first().user == user
    assert Image.objects.first().small_thumbnail is not None
    assert Image.objects.first().large_thumbnail is not None


def test_image_deletion(image):
    image.delete()
    assert Image.objects.count() == 0
