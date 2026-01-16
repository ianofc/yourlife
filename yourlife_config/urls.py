
from django.contrib import admin
from django.urls import path, include
from .views_api import receive_sync

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/social/sync-user/', receive_sync),
    path('', include('social.urls')),
]
