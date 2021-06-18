from django.core.management.base import BaseCommand
from calls.models import ArchiveStatus


class Command(BaseCommand):
    help = 'Create default data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Start create Archive statuses.')
        ArchiveStatus.objects.create(id=0, name='In process', css_style='text-warning')
        ArchiveStatus.objects.create(id=1, name='Success', css_style='text-success')
        ArchiveStatus.objects.create(id=2, name='Failed', css_style='text-danger')
        self.stdout.write('Archive statuses has been created')
