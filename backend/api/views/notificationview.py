from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from ..models.notificationmodel import Notification
from ..serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
            Get all notifications for a user.
            The user id is passed as GET parameter.
        """
        queryset = Notification.objects.all()
        uid = self.request.query_params.get("uid", None)
        if(uid is not None):
            queryset = queryset.filter(user=uid)
            queryset = queryset.order_by("seen")
            
        return queryset
