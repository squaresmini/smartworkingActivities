from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from smartworkingActivities.swapi import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'activities', views.ActivityApiViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'activity-types', views.ActivityTypeViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path(r'import-json/',views.ImportJson.as_view(), name = 'import-json'),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
