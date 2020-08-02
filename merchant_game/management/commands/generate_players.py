import random

from django.core.management.base import BaseCommand, CommandError
from merchant_game.models import Player


class Command(BaseCommand):
    help = 'Populates the database with players. Removes pre-existing data'

    def handle(self, *args, **options):
        Player.objects.all().delete()
        for player_code_count in range(80):
            p = Player(code=random.randrange(100000, 999999))
            p.save()
        self.stdout.write(self.style.SUCCESS('Successfully generated players'))
