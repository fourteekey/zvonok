import logging
import os
import random
import zipfile
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from .models import *

logger = get_task_logger(__name__)


@shared_task(name="create_archive")
def create_archive_task(archive_id, calls_ids, user_id):
    archive_root = f'{settings.MEDIA_ROOT}/archives'

    # Generate archive name
    filepath = ''
    if user_id:
        filepath += f'{user_id}/'
        if not os.path.isdir(f'{archive_root}/{user_id}'): os.mkdir(f'{archive_root}/{user_id}')
    filepath += f'{random.randint(1000, 999999)}.zip'
    while os.path.isfile(f'{archive_root}/{filepath}'):
        filepath = ''
        if user_id: filepath += f'{user_id}/'
        filepath += f'{random.randint(1000, 999999)}.zip'

    archive = UserArchives.objects.get(id=archive_id)
    archive.filepath = filepath
    archive.save()

    calls = AtsCall.objects.filter(id__in=calls_ids)
    with zipfile.ZipFile(f'{archive_root}/{filepath}', 'a') as myzip:
        for call in calls:
            try:
                myzip.write(call.get_call_file_path(), f'{call.id}.mp3')
            except Exception as e:
                logging.error('Cannot find file. ', e, '| PATH TO FILE: ', call.get_call_file_path())
                archive.status = ArchiveStatus.objects.get(id=2)
                archive.save()
                return

    archive.status = ArchiveStatus.objects.get(id=1)
    archive.save()
