from django.urls import include, path, re_path
from .views import CustomUserViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register('users', CustomUserViewSet)
urlpatterns = [
    path('', include(router.urls)),
    re_path(r"^auth/", include("djoser.urls.base")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
]