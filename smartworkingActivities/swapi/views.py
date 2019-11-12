from smartworkingActivities.swapi import models, permissions, serializers
from django.contrib.auth.models import User
from rest_framework import viewsets,generics,parsers,status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action,permission_classes
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView
from datetime import datetime,date
from django.db import transaction

import csv, codecs


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()


class ActivityTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ActivityTypeSerializer
    queryset = models.ActivityType.objects.all()


class ActivityApiViewSet(viewsets.ModelViewSet):
    queryset = models.Activity.objects.all()
    serializer_class = serializers.ActivitySerializer

    def get_permissions(self):
        if self.action == 'list_all':
            permission_classes = [permissions.IsBoss]
        else:
            permission_classes = [permissions.IsOwner]

        return [permission() for permission in permission_classes]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = serializers.ActivitySerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return models.Activity.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['get'],detail=False,url_name='list-all',url_path='list-all')
    def list_all(self,request):
        activities = models.Activity.objects.all().order_by('user')
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page,many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities,many=True)
        return Response(serializer.data)


class ImportJson(APIView):
    parser_class=[parsers.FileUploadParser]

    @transaction.atomic
    def post(self, request,format=None):
        if not request.FILES['file']:
            raise ParseError("Empty content")

        file_obj = request.FILES['file']

        reader = list(csv.reader(codecs.iterdecode(file_obj, 'ISO-8859-1',errors='ignore'), delimiter=';'))

        for row in reader[1:]:
            user = User.objects.get(username=row[0].lower())
            type = models.ActivityType.objects.get(label=row[1].upper())
            hours = float(row[5].replace(',','.'))
            jira_id = row[2] if row[2] else None
            models.Activity.objects.create(
                user = user,
                type = type,
                jira_id=jira_id,
                description=row[3],
                smartworking_date=datetime.strptime(row[4],'%d/%m/%Y').date(),
                hours=hours
            )

        file_obj.close()
        return Response(status=status.HTTP_201_CREATED)

