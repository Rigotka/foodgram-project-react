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
from .permissions import IsOwnerOrReadOnly
from .models import Subscription, User
from .paginator import VariablePageSizePaginator
from .serializers import SubscriptionSerializer, UserSerializer,


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = PageNumberPagination

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        data = {
            'user': user.id,
            'author': author.id,
        }
        serializer = SubscriptionSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscribe = get_object_or_404(
            Subscription, user=user, author=author
        )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

# class SubscribeViewSet(APIView):
#     def get(self, request, author_id):
#         user = request.user
#         data = {
#             'user': user.id,
#             'author': author_id
#         }
#         serializer = SubscriptionSerializer(
#             data=data,
#             context={'request': request}
#         )
#         if not serializer.is_valid():
#             return Response(
#                 serializer.errors,
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         serializer.save()
#         return Response(
#             serializer.data,
#             status=status.HTTP_201_CREATED
#         )

#     def delete(self, request, author_id):
#         user = request.user
#         author = get_object_or_404(User, id=author_id)
#         get_object_or_404(Subscription, user=user, author=author).delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class ListSubscribeViewSet(generics.ListAPIView):
#     queryset = User.objects.all()
#     permission_classes = [IsAuthenticated, ]
#     serializer_class = ShowSubscriptionSerializer

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update({'request': self.request})
#         return context

#     def get_queryset(self):
#         user = self.request.user
#         return User.objects.filter(following__user=user)
