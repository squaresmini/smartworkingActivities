from django.contrib.auth.models import User
from rest_framework import serializers,status
from smartworkingActivities.swapi import models
from datetime import date
from django.utils import timezone


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'id', 'username']


class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.ActivityType
        fields='__all__'


class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    type = serializers.SlugRelatedField(slug_field='label', queryset=models.ActivityType.objects.all())
    smartworking_date = serializers.DateField(default=timezone.now,initial=date.today(),format='%d/%m/%Y', input_formats=['%d/%m/%Y'])

    def validate_smartworking_date(self,value):
        if value>date.today():
            raise serializers.ValidationError("Smartworking date is in the future!",code=status.HTTP_412_PRECONDITION_FAILED)
        return value

    class Meta:
        model = models.Activity
        fields = ['user', 'type', 'jira_id', 'description', 'smartworking_date', 'hours']
