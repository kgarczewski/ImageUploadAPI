"""ImageUploadAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ImageUploadAPI.views import ImageView, ImageCreateView,  GenerateExpiringUrlView, ServeImageView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
from django.conf.urls.static import static
from django.conf import settings
from .utils import serve_thumbnail, generate_expiring_url

router.register('my_images', ImageView, 'imagelist')
router.register('add_image', ImageCreateView, 'addimage')
urlpatterns = [
    path('my_images/<int:image_id>/generate_expiring_url/', GenerateExpiringUrlView.as_view(), name='expiration_link'),
    path('<int:image_id>/serve_image/<str:signature>/', ServeImageView.as_view(), name='serve-image'),
    path('images/<int:image_id>/generate_expiring_url/', generate_expiring_url, name='image-detail'),
    path('thumbnail/<str:thumbnail_path>', serve_thumbnail, name='serve-thumbnail'),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
