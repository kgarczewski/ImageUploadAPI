from ImageUploader.models import Image
from .serializers import ImageCreateSerializer, ImageSerializer
from mimetypes import guess_type
import datetime

from django.utils import timezone
from django.urls import reverse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.validators import validate_integer
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView

from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.viewsets import ViewSetMixin


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class CustomLoginView(LoginView):
    template_name = 'login_view.html'


class CustomLogout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'})


class ImagePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class ImageView(ViewSetMixin, generics.ListAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    template_name = 'image_view.html'
    renderer_classes = [TemplateHTMLRenderer]
    pagination_class = ImagePagination


    def list(self, request, *args, **kwargs):
        viewset = ImageView(**{'request': request})
        extra_actions = viewset.get_extra_actions()
        if request is None:
            return Response(status=400, data={'message': 'Bad Request'})

        images = self.get_queryset().filter(user=request.user)
        # get paginated results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(images, request)
        next = paginator.get_next_link()
        previous = paginator.get_previous_link()

        image_data = []

        for image in page:

            data = {
                'id': image.id if request.user.account_tier.original_file else '',
                'image': image.image,
                'small_thumbnail': image.small_thumbnail if request.user.account_tier.thumbnail_200 else '',
                'large_thumbnail': image.large_thumbnail if request.user.account_tier.thumbnail_400 else '',
                'expiration_link': image.expiration_link if request.user.account_tier.expiring_links else '',
                'expiration_date': image.expiration_date
            }

            image_data.append(data)
        # determine if there are more pages
        has_more_pages = len(page) == paginator.page_size

        context = {
            'images': image_data, 'page': page, 'has_more_pages': has_more_pages, 'next': next, 'previous': previous
        }
        return Response(context, template_name='image_view.html')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class ImageCreateView(ViewSetMixin, generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class GenerateExpiringUrlView(APIView):
    def post(self, request, image_id):
        # Validate the input.
        try:
            expiration_seconds = int(request.POST.get('expiration_seconds'))
            validate_integer(expiration_seconds)
            if not 10 <= expiration_seconds <= 30000:
                raise ValueError('Invalid expiration time.')
        except (ValueError, TypeError):
            raise Http404('Invalid expiration time.')

        # Retrieve the image.
        image = get_object_or_404(Image, pk=image_id)

        # Generate the expiration timestamp.
        expiration_time = timezone.now() + timezone.timedelta(seconds=expiration_seconds)

        # Create the signed URL.
        signer = TimestampSigner()
        signed_value = signer.sign(str(image_id) + str(expiration_time.timestamp()))
        url = reverse('serve-image', kwargs={'image_id': image_id, 'signature': signed_value})

        # Create the expiration token
        expiration_token = signer.sign(str(expiration_seconds))

        # Save the expiration token to the image model
        image.expiration_token = expiration_token
        image.expiration_date = expiration_time
        image.expiration_link = request.build_absolute_uri(url)
        image.save()

        # Construct the full URL.
        full_url = request.build_absolute_uri(url)

        if url:
            return Response({"url": full_url, "expired": False})
        else:
            return Response({"detail": "Not found.", "expired": True}, status=status.HTTP_404_NOT_FOUND)


class ServeImageView(APIView):
    def get(self, request, image_id, signature):
        # Retrieve the image.
        image = get_object_or_404(Image, pk=image_id)

        # Check if the user is authorized to access the image.

        if image.expiration_date and image.expiration_date < timezone.now():
            return Response({'detail': 'The link has expired.'}, status=404)

        # Validate the signature.
        signer = TimestampSigner()
        try:
            value = signer.unsign(signature, max_age=30000)
            timestamp = float(str(value)[len(str(image_id)):])
            expiration_time = timezone.make_aware(datetime.datetime.fromtimestamp(timestamp), timezone.utc)
            if expiration_time <= timezone.now():
                raise BadSignature('Signature has expired.')
        except (BadSignature, ValueError, SignatureExpired):
            raise Http404('Invalid signature.')

        # Serve the image.
        content_type = guess_type(image.image.name)[0]
        if not content_type:
            content_type = 'application/octet-stream'
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = 'filename="{}"'.format(image.image.name)
        response.write(image.image.read())
        return response
