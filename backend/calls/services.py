import os
import random
from django.core.files.storage import FileSystemStorage
from datetime import datetime

from .serializers import *
from .tasks import *


def get_user_from_request(request):
    if request.user.is_anonymous: user = None
    else: user = request.user
    return user


def get_ats_campaigns():
    ats_campaigns = AtsCampaign.objects.all()
    return AtsCampaignSerializer(ats_campaigns, many=True).data


def get_archives(user, ats_campaign_id):
    if user:
        archives = UserArchives.objects.filter(user=user)
    else:
        archives = UserArchives.objects.filter(user__isnull=True, ats_campaign=ats_campaign_id)[:1]

    return ArchivesSerializer(archives, many=True).data


def get_ats_calls(ats_campaign_id, user):
    ats_calls = AtsCall.objects.filter(ats_campaign_id=ats_campaign_id)
    if user: ats_calls = ats_calls.filter(user=user)

    return AtsCallSerializer(ats_calls, many=True).data


def save_calls(ats_campaign_id, files, user):
    list_new_ats_calls = []
    f = FileSystemStorage()
    for data_file in files:
        # В идеале. в продакшине
        ats_campaign = AtsCampaign.objects.filter(id=ats_campaign_id)
        if not ats_campaign: return

        ats_folder_path = ats_campaign[0].get_or_create_ats_folder_path()

        file_id = f"{datetime.now().strftime('%y%m%d')}{random.randint(1000, 999999)}"

        # Check on filename conflict
        while os.path.isfile(f'{ats_folder_path}/{file_id}.mp3'):
            file_id = f"{datetime.now().strftime('%y%m%d')}{random.randint(1000, 999999)}"

        new_ats_call = AtsCall.objects.create(id=int(file_id), ats_campaign=ats_campaign[0], user=user)
        list_new_ats_calls.append(new_ats_call)
        f.save(f'{ats_folder_path}/{file_id}.mp3', data_file)
    return AtsCallSerializer(list_new_ats_calls, many=True).data


def get_call_to_download(user, ats_campaign_id, ats_call_id):
    ats_call = AtsCall.objects.filter(id=ats_call_id, ats_campaign=ats_campaign_id)
    # Add filter to authenticated users
    if user: ats_call = ats_call.filter(user=user)
    if not ats_call: return
    return AtsCallSerializer(ats_call[0]).data


def create_archive(ats_campaign_id, user):
    calls = AtsCall.objects.filter(ats_campaign=ats_campaign_id)
    if user: calls = calls.filter(user=user)
    calls_ids = calls.values_list('id', flat=True)
    if not calls_ids: return

    if user:
        old_archive = UserArchives.objects.filter(ats_campaign=ats_campaign_id, user=user)[:1]
    else:
        old_archive = UserArchives.objects.filter(ats_campaign=ats_campaign_id, user__isnull=True)[:1]

    if old_archive and old_archive[0].count_calls == calls.count():
        old_archive[0].updated = datetime.now()
        return 1
    elif not user and old_archive and old_archive[0].status_id != 0 \
            and os.path.isfile(old_archive[0].get_archive_file_path()):
        os.remove(old_archive[0].get_archive_file_path())
        old_archive.remove()

    archive = UserArchives.objects.create(
        updated=datetime.now(),
        count_calls=len(calls_ids),
        ats_campaign_id=ats_campaign_id,
        user=user)
    if user: user_id = user.id
    else: user_id = None

    task = create_archive_task.delay(archive_id=archive.id, calls_ids=tuple(calls_ids), user_id=user_id)
    archive.task_id = task.id
    archive.save()

    return 1
