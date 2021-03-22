from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from bids.models import Item, Bid
from bids.tests.builder import Builder


class Command(BaseCommand):
    help = "Creates test data, deletes all previous existing data in item and bid"

    def handle(self, *args, **options):
        builder = Builder()
        self.stdout.write("Deleting all existing data")
        Item.objects.all().update(best_bid=None)
        Bid.objects.all().delete()
        Item.objects.all().delete()
        get_user_model().objects.filter(username__startswith="user_").delete()
        users = []
        items = []
        for i in range(10):
            users.append(builder.user(username=f"user_{i}"))
            items.append(builder.item(name=f"item_{i}", description=f"description_{i}"))

        for item in items:
            for number, user in enumerate(users):
                builder.bid(item=item, user=user, amount=Decimal(number + 1))

        self.stdout.write(self.style.SUCCESS("Successfully Test data"))
