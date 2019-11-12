from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.test import force_authenticate
from rest_framework import status
from smartworkingActivities.swapi.models import Activity, ActivityType
from django.contrib.auth.models import User, AnonymousUser
from smartworkingActivities.swapi import serializers
import json
from rest_framework.exceptions import ErrorDetail
from datetime import date, timedelta
import os

class SwActivitiesTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.myuser = User.objects.create_user(username='a208782')
        cls.user2 = User.objects.create_user(username='a141882')
        cls.user_boss = User.objects.create_user(username='a133982')
        cls.type = ActivityType.objects.create(label='PRJ')
        cls.activity = Activity.objects.create(
            user=cls.myuser,
            type=cls.type,
            jira_id=1,
            description='Attività',
            smartworking_date=date.today(),
            hours=5.5)

    def test_not_auth_activities(self):
        url = reverse('activitytype-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_own_activities(self):
        url = reverse('activity-list')
        user = User.objects.get(username='a208782')
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data[0]['type'],'PRJ')
        self.assertEqual(response.data[0]['user'],'a208782')
        self.assertEqual(response.data[0]['jira_id'],1)
        self.client.force_authenticate(user=None)

    def test_read_other_activities(self):
        url = reverse('activity-list')
        user = User.objects.get(username='a141882')
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),0)
        self.client.force_authenticate(user=None)

    def test_read_all_activities_boss(self):
        url = reverse('activity-list-all')
        user = User.objects.get(username='a133982')
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),1)
        self.assertEqual(response.data['results'][0]['type'],'PRJ')
        self.assertEqual(response.data['results'][0]['user'],'a208782')
        self.assertEqual(response.data['results'][0]['jira_id'],1)
        self.client.force_authenticate(user=None)

    def test_read_all_activities_other_user(self):
        url = reverse('activity-list-all')
        user = User.objects.get(username='a208782')
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=None)

    def test_create_activity_ok(self):
        url = reverse('activity-list')
        user = User.objects.get(username='a208782')
        self.client.force_authenticate(user=user)
        data={
            'type': 'PRJ',
            'jira_id':2,
            'description':'Attività 2',
            'smartworking_date':date.today().strftime('%d/%m/%Y'),
            'hours':3.0
        }
        request_data = json.dumps(data)
        response = self.client.post(url,data=request_data,content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        activity_created = Activity.objects.get(jira_id=2)
        self.assertIsNotNone(activity_created)
        self.assertEqual(activity_created.user,user)
        self.client.force_authenticate(user=None)

    def test_create_activity_ko(self):
        url = reverse('activity-list')
        user = User.objects.get(username='a208782')
        self.client.force_authenticate(user=user)
        data = {
            'type': 'PRJ',
            'jira_id': 3,
            'description': 'Attività 3',
            'smartworking_date': (date.today()+timedelta(days=1)).strftime('%d/%m/%Y'),
            'hours': 3.0
        }
        request_data = json.dumps(data)
        response = self.client.post(url, data=request_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(type(response.data['smartworking_date'][0]),ErrorDetail)

        self.assertRaises(Activity.DoesNotExist,Activity.objects.get,jira_id=3)
        self.client.force_authenticate(user=None)
# Create your tests here.
