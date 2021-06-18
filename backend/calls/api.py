from django.urls import path
from . import views


urlpatterns = [
    path('call', views.CallAPIView.as_view(), name='call'),
    path('archives', views.ArchiveAPIView.as_view(), name='archive'),
]
