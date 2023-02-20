from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Create a superuser with account_tier.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--email', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--account_tier', required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password']
        account_tier_name = options['account_tier']

        # Get the account tier object
        Plan = apps.get_model('ImageUploader', 'Plan')
        try:
            account_tier = Plan.objects.get(name=account_tier_name)
        except Plan.DoesNotExist:
            print(f"Error: Plan with name {account_tier_name} does not exist.")
            return

        # Create the superuser
        user = User.objects.create_superuser(username=username, email=email, password=password, account_tier=account_tier)
        print(f"Created superuser {username} with account tier {account_tier_name}.")