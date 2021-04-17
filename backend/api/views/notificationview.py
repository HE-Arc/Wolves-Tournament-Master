from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models.notificationmodel import Notification
from ..serializers import NotificationSerializer
from django.utils import timezone 


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        """
            Create a new notification from the request and add the creation date.
        """

        data = request.data
        data["creationDate"] = timezone.now()

        serializer = self.serializer_class(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            notification = Notification.objects.create(**serializer.validated_data)
            notification.save()

            return Response(self.get_serializer(notification).data, status=status.HTTP_200_OK)

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
