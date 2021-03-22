import asyncio
import logging

import aiohttp

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.tokens import RefreshToken

from bids.models import Item, Bid
from bids.tests.builder import Builder


logger = logging.getLogger(__name__)


async def make_post(user, item, amount):
    logger.info(f"Calling {user} amount {amount}")
    token = RefreshToken.for_user(user)
    jwt = str(token.access_token)
    async with aiohttp.ClientSession(
        headers={
            "Accept": "application/json",
            "Content-type": "application/json",
            "Authorization": f"Bearer {jwt}",
        }
    ) as session:
        async with session.post(
            "http://localhost:8000/api/bids/",
            json={
                "item": item.id,
                "amount": amount,
            },
        ) as response:
            data = await response.text()
            print(f"Executed post! {data}")


class Command(BaseCommand):
    help = "Perform some concurrent POST requests to test concurrency"

    def clean_up(self, item, users):
        logger.info("Cleaning data")
        Bid.objects.filter(user__in=users).delete()
        get_user_model().objects.filter(
            username__in=[user.username for user in users]
        ).delete()
        Item.objects.filter(pk=item.pk).delete()
        logger.info("Cleaned data")

    def handle(self, *args, **options):
        builder = Builder()
        total_users = 5
        logger.info("Creating test data")
        item = builder.item(name="concurrency", description="concurrency")
        users = [
            builder.user(username=f"concurrency_{i}", password="password")
            for i in range(total_users)
        ]
        logger.info("Created test data")

        tasks = []
        for number, user in enumerate(users):
            tasks.append(make_post(user, item, number + 1))
        loop = asyncio.get_event_loop()
        logger.info("Performing %s concurrent POST requests", total_users)
        loop.run_until_complete(asyncio.wait(tasks))
        # check the item best bid amount is total_users
        item.refresh_from_db()
        logger.info(f"Item best bid amount is {item.best_bid.amount}")
        self.clean_up(item, users)
