from django.core.management.base import BaseCommand, CommandError
from bids.models import Item


class Command(BaseCommand):
    help = "Creates an item"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str)
        parser.add_argument("description", type=str)

    def handle(self, *args, **options):
        name = options["name"]
        description = options["description"]
        Item.objects.update_or_create(name=name, defaults={"description": description})
        self.stdout.write(
            self.style.SUCCESS('Successfully created/updated item "%s"' % name)
        )
