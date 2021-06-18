from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create superuser'

    def add_arguments(self, parser):
        parser.add_argument('-username', type=str, help='username')

    def handle(self, *args, **kwargs):
        username = kwargs['username']

        if not username:
            self.stdout.write('Значение \'-u VALUE\' обязательно.')
            return
        self.stdout.write('Start create superuser.')
        user = get_user_model().objects.create_superuser(username=username)
        user.set_password(username)
        user.is_active = True
        user.is_admin = True
        user.save()

        self.stdout.write('superuser has been created')

