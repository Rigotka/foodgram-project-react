from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import SubscribeViewSet, CustomUserViewSet, ListSubscribeViewSet

router = DefaultRouter()

router.register('users', CustomUserViewSet)
urlpatterns = [
    path('', include(router.urls)),
    re_path("auth/", include("djoser.urls.base")),
    re_path("auth/", include("djoser.urls.authtoken")),
]
