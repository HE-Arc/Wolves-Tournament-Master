from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from ..models.notificationmodel import Notification
from ..serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Get all notification by user id
    def get_queryset(self):
        queryset = Notification.objects.all()
        uid = self.request.query_params.get("uid", None)
        if(uid is not None):
            queryset = queryset.filter(user=uid)
            queryset = queryset.order_by("seen")
            #queryset = queryset.filter(seen=False)
        return queryset
