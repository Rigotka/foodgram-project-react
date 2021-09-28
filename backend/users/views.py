from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import SubscriptionSerializer, UserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny, ]
    pagination_class = PageNumberPagination

    @action(methods=['get', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {"Ошибка": "Уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow = Subscription.objects.filter(user=user, author=author)
        if request.method == 'GET':
            if not follow.exists():
                new_follow = Subscription.objects.create(user=user,
                                                         author=author)
                new_follow.save()
            serializer = SubscriptionSerializer(instance=author,
                                                context={'request': request})
            return Response(serializer.data)
        elif request.method == 'DELETE':
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        user = self.request.user
        users = User.objects.filter(subscription__user=user)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(users, request)
        serializer = SubscriptionSerializer(result_page, many=True,
                                            context={'request': request})
        return paginator.get_paginated_response(serializer.data)
