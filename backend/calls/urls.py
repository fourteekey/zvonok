from django.urls import path, include, re_path
from . import views
from django.conf import settings

urlpatterns = [
    path('login/', views.auth_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.index_view, name='index'),
    path('archives/', views.archives_view, name='archives'),
    path('archives/<int:ats_campaign_id>', views.archives_view, name='archives_ats_campaign'),
    path('<int:ats_campaign_id>/calls', views.calls_view, name='campaign_calls'),
]
