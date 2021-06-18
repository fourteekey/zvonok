import os

from rest_framework import permissions
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from . import services
from .custom_schemas import *
from .models import *
from .serializers import *
from .tasks import *


def auth_view(request):
    if request.user.is_anonymous and request.POST:
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('index')
        return render(request, 'login.html', {'error': 'Invalid login or password.'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def index_view(request):
    return render(request, 'index.html', {'campaigns': services.get_ats_campaigns()})


def archives_view(request, ats_campaign_id=None):
    user = services.get_user_from_request(request)

    archives = services.get_archives(user=user, ats_campaign_id=ats_campaign_id)
    return render(request, 'archives.html', {'archives': archives})


def calls_view(request, ats_campaign_id):
    user = services.get_user_from_request(request)
    calls = services.get_ats_calls(ats_campaign_id=ats_campaign_id, user=user)
    return render(request, 'calls.html', {'ats_campaign_id': ats_campaign_id, 'calls': calls})


def download_call(request, ats_campaign_id, date_prefix, ats_call_id):
    user = services.get_user_from_request(request)
    call = services.get_call_to_download(user, ats_campaign_id, ats_call_id)
    if call:
        filepath = f'{settings.MEDIA_ROOT}/calls/{ats_campaign_id}/{ats_call_id}.mp3'
        if os.path.exists(filepath):
            with open(filepath, 'rb') as fh:
                # content_type = "audio/mpeg" # Этот тип будет открываться трек в браузере, а не скачивать.
                response = HttpResponse(fh.read(), content_type="application/audio")
                response['Content-Disposition'] = f'inline; filename={ats_call_id}.mp3'
                return response

    return HttpResponse(status=status.HTTP_404_NOT_FOUND)


class CallAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description='Upload audio files.',
        manual_parameters=[openapi.Parameter('ats_campaign_id', openapi.IN_QUERY, type='number', required=True)],
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={'files': openapi.Schema(type=openapi.TYPE_FILE)}),
        responses={200: AtsCallSerializer, 400: error_schema})
    def post(self, request):
        ats_campaign_id = request.query_params.get('ats_campaign_id', None)
        files = request.data.getlist('files', None)

        if not ats_campaign_id:
            return Response({'detail': 'Missing required params: \'ats_campaign_id\'.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not files:
            return Response({'detail': 'Invalid request body. Missing \'files\'.'},
                            status=status.HTTP_400_BAD_REQUEST)

        calls_serializer = services.save_calls(ats_campaign_id=ats_campaign_id, files=files, user=request.user)
        if not calls_serializer: return Response({'detail': 'Server error.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(calls_serializer)


class ArchiveAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description='Create archive.',
        manual_parameters=[openapi.Parameter('ats_campaign_id', openapi.IN_QUERY, type='number', required=True)],
        responses={200: url_schema, 400: error_schema})
    def post(self, request):
        ats_campaign_id = request.query_params.get('ats_campaign_id', None)
        user = services.get_user_from_request(request)
        if not ats_campaign_id:
            return Response({'detail': 'Missing required params: \'ats_campaign_id\'.'},
                            status=status.HTTP_400_BAD_REQUEST)
        archive = services.create_archive(ats_campaign_id=ats_campaign_id, user=user)
        if not archive: return Response({'detail': 'Cannot create archive.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'url': reverse('archives_ats_campaign', kwargs={"ats_campaign_id": ats_campaign_id})})
