import logging
import requests
import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.tokens import RefreshToken

from bids.models import Item, Bid
from bids.tests.builder import Builder


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Creates an item, 1000 users, and performs 1000 POST to"
        " create bids, one per user"
    )

    def clean_up(self, item, users):
        logger.info("Cleaning data")
        Bid.objects.filter(user__in=users).delete()
        get_user_model().objects.filter(
            username__in=[user.username for user in users]
        ).delete()
        Item.objects.filter(pk=item.pk).delete()
        logger.info("Cleaned data")

    def handle(self, *args, **options):
        logger.info("Creating test data")
        builder = Builder()
        total_users = 1000
        item = builder.item(name="performance", description="performance")
        users = [
            builder.user(username=f"performance_{i}", password="password")
            for i in range(total_users)
        ]
        logger.info("Created test data")
        total_time = 0
        amount = 1
        logger.info("Performing %s POST requests", total_users)
        for user in users:
            token = RefreshToken.for_user(user)
            jwt = str(token.access_token)
            start_time = time.time()
            requests.post(
                "http://localhost:8000/api/bids/",
                json={
                    "item": item.id,
                    "amount": amount,
                },
                headers={
                    "Accept": "application/json",
                    "Content-type": "application/json",
                    "Authorization": f"Bearer {jwt}",
                },
            )
            duration = time.time() - start_time
            total_time = total_time + duration
            amount = amount + 1
        logger.info("Created %s bids in %s seconds", total_users, total_time)
        logger.info("Average response time %s ms", total_time / total_users * 1000)
        self.clean_up(item, users)
