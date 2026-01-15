from django.urls import path
from .views import PublicRegisterView

app_name = 'yourlife_global'

urlpatterns = [
    path('join/', PublicRegisterView.as_view(), name='global_join'),
]
