from rest_framework import serializers
from .models import *


class AtsCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtsCampaign
        fields = ('id',)


class AtsCallSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%Y-%d-%m %H:%M")
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = AtsCall
        fields = ('id', 'ats_campaign', 'user', 'created', 'download_url',)

    @staticmethod
    def get_download_url(obj):
        return obj.get_call_record_url(obj.ats_campaign.id, obj.id)


class ArchivesSerializer(serializers.ModelSerializer):
    updated = serializers.DateTimeField(format="%Y-%d-%m %H:%M:%S")
    status = serializers.CharField(source='status.name')
    status_id = serializers.IntegerField(source='status.id')
    download_url = serializers.SerializerMethodField()
    css_style = serializers.CharField(source='status.css_style')

    class Meta:
        model = UserArchives
        fields = ('id', 'updated', 'count_calls', 'ats_campaign', 'user', 'task_id',
                  'status', 'status_id', 'download_url', 'css_style')

    @staticmethod
    def get_download_url(obj):
        # Вообще это можно было вынести прям в шаблон.
        if obj.status.id == 1:
            download_url = f'{settings.MEDIA_URL}archives/'
            download_url += obj.filepath
            return download_url

        return None
