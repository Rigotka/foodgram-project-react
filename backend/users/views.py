from os import execlp
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, generics
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView

from recipes.permissions import IsAuthorOrReadOnly

from .models import Subscription, User
from .paginator import VariablePageSizePaginator
from .serializers import SubscriptionSerializer, UserSerializer, ShowSubscriptionSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthorOrReadOnly]


class SubscribeViewSet(APIView):
    def get(self, request, author_id):
        user = request.user
        data = {
            'user': user.id,
            'author': author_id
        }
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        get_object_or_404(Subscription, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListSubscribeViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = ShowSubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(author__user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
