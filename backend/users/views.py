from os import execlp
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
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
from .serializers import SubscriptionSerializer, UserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthorOrReadOnly]

#     @action(methods=['get', 'delete'], detail=True,
#             permission_classes=[IsAuthenticated])
#     def subscribe(self, request, id=None):
#         user = self.request.user
#         author = get_object_or_404(User, id=id)

#         if request.method == 'GET':
#             data = {
#                 'user': user.id,
#                 'author': author.id
#             }
#             serializer = SubscriptionSerializer(data=data, context={'request': request})
#             if not serializer.is_valid():
#                 return Response(
#                     serializer.errors,
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         obj = get_object_or_404(Subscription, user=user, author=author)
#         if obj:
#             obj.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response({"error": "Вы не подписаны на этого пользователя"}, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=False)
#     def subscriptions(self, request):
#         user = self.request.user
#         users = User.objects.filter(subscription__user=user)
#         paginator = PageNumberPagination()
#         paginator.page_size = 3
#         result_page = paginator.paginate_queryset(users, request)
#         serializer = SubscriptionSerializer(result_page, many=True,
#                                             context={'request': request})
#         return paginator.get_paginated_response(serializer.data)


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
