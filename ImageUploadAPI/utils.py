import io
from django.core.files.base import ContentFile
from PIL import Image as PILImage
from django.http import HttpResponse
from django.urls import reverse


def create_thumbnail(image, height):
    original_width, original_height = image.size
    aspect_ratio = original_width / original_height
    thumbnail_width = int(height * aspect_ratio)
    thumbnail = image.resize((thumbnail_width, height), resample=PILImage.LANCZOS)
    return thumbnail


def create_small_thumbnail(image, size):
    small_thumbnail = create_thumbnail(image, size)
    small_thumb_io = io.BytesIO()
    small_thumbnail.save(small_thumb_io, format='JPEG')
    return ContentFile(small_thumb_io.getvalue(), 'small_thumbnail.jpeg')


def create_large_thumbnail(image, size):
    large_thumbnail = create_thumbnail(image, size)
    large_thumb_io = io.BytesIO()
    large_thumbnail.save(large_thumb_io, format='JPEG')
    return ContentFile(large_thumb_io.getvalue(), 'large_thumbnail.jpeg')


def serve_thumbnail(thumbnail_path):
    """
    Serve the thumbnail from the media directory.
    """
    with open(f"media/{thumbnail_path}", "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")


def generate_expiring_url(request, image_id, expiration_seconds, expiration_token):
    url = reverse('image-detail', args=[image_id])
    expiration_link = request.build_absolute_uri(url) + f'?expires_in={expiration_seconds}&expiration_token={expiration_token}'
    return expiration_link
