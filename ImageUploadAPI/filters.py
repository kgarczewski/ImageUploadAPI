import django_filters
from django_filters import rest_framework as filters
from ImageUploader.models import Image
from django.db.models import ImageField


# class ImageFilter(django_filters.FilterSet):
#     class Meta:
#         model = Image
#         fields = ['id', 'image', 'user', 'small_thumbnail', 'large_thumbnail']
#         filter_overrides = {
#             ImageField: {
#                 'filter_class': django_filters.CharFilter,
#                 'extra': lambda f: {
#                     'lookup_expr': 'exact',
#                 },
#             },
#         }
#
# class CustomFilterBackend(filters.DjangoFilterBackend):
#     def get_filterset_class(self, view, queryset=None):
#         filterset = super().get_filterset_class(view, queryset)
#         filter_exclude = getattr(view, 'filter_exclude', None)
#         for x in filter_exclude:
#             filterset.declared_filters.pop(x, None)
#         return filterset
