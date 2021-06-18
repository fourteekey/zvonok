from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from calls.views import download_call

schema_view = get_schema_view(openapi.Info(title="CsvGenerator API", default_version='v1'), url=settings.API_URL)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/', include('api.api', namespace='api_urls')),

    path('admin/', admin.site.urls),
    path('', include('calls.urls'), name='index'),

    path(f'{settings.AUDIO_BASE_URL}directcdr/<int:ats_campaign_id>/<int:date_prefix>/<int:ats_call_id>.mp3',
         download_call, name='download_audio')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
