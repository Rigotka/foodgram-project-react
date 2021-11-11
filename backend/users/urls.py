from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import SubscribeViewSet, CustomUserViewSet, ListSubscribeViewSet

router = DefaultRouter()

router.register('users', CustomUserViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:author_id>/subscribe/',
         SubscribeViewSet.as_view(), name='subscribe'),

    path('users/subscriptions/',
         ListSubscribeViewSet.as_view(), name='subscriptions'),

    re_path("auth/", include("djoser.urls.base")),
    re_path("auth/", include("djoser.urls.authtoken")),
]
