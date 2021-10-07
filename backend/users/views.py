from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import SubscriptionSerializer, UserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @action(methods=['get', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        
        if request.method == 'GET':
            data = {
                'user': user.id,
                'author': author.id
            }
            serializer = SubscriptionSerializer(data=data, context={'request': request})
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            obj = get_object_or_404(Subscription, user=user, author=author)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        user = self.request.user
        users = User.objects.filter(subscription__user=user)
        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(users, request)
        serializer = SubscriptionSerializer(result_page, many=True,
                                            context={'request': request})
        return paginator.get_paginated_response(serializer.data)
