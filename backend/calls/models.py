import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


class ArchiveStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    css_style = models.CharField(max_length=100)

    class Meta:
        db_table = 'archive_status'

    def __str__(self):
        return self.name


class AtsCampaign(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'ats_campaign'

    def get_or_create_ats_folder_path(self):
        ats_folder_path = f'{settings.MEDIA_ROOT}/calls/{self.id}'
        if not os.path.isdir(ats_folder_path): os.mkdir(ats_folder_path)
        return ats_folder_path

    def __str__(self):
        return str(self.id)


class AtsCall(models.Model):
    id = models.BigIntegerField(primary_key=True)
    ats_campaign = models.ForeignKey('AtsCampaign', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ats_call'
        ordering = ('-created',)

    def get_call_file_path(self):
        return f'{settings.MEDIA_ROOT}/calls/{self.ats_campaign}/{self.id}.mp3'

    @staticmethod
    def get_call_record_url(ats_campaign_id, ats_call_id):
        date_prefix = str(ats_call_id)[:6]
        return f'/{settings.AUDIO_BASE_URL}directcdr/{ats_campaign_id}/{date_prefix}/{ats_call_id}.mp3'


class UserArchives(models.Model):
    filepath = models.CharField(max_length=150, default=None, null=True)
    updated = models.DateTimeField(auto_now=True)
    count_calls = models.IntegerField()
    ats_campaign = models.ForeignKey('AtsCampaign', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, default=None)

    task_id = models.CharField(max_length=100, default=None, null=True)
    status = models.ForeignKey('ArchiveStatus', on_delete=models.DO_NOTHING, default=0)

    def get_archive_file_path(self):
        return f'{settings.MEDIA_ROOT}/archives/{self.filepath}.zip'

    class Meta:
        db_table = 'user_archives'
        ordering = ('-updated',)

    def __str__(self):
        return str(self.id)
