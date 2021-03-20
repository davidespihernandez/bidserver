from decimal import Decimal

from django.test import TestCase
from freezegun import freeze_time

from bids.serializers import ItemSerializer, BidSerializer
from bids.tests.builder import Builder


@freeze_time("1975-01-02T00:00:00Z")
class ItemSerializerTestCase(TestCase):
    builder = Builder()

    def setUp(self) -> None:
        self.user = self.builder.user()
        self.item = self.builder.item()
        self.best_bid = self.builder.bid(
            item=self.item, user=self.user, amount=Decimal(1)
        )
        self.item.best_bid = self.best_bid
        self.expected = {
            "id": self.item.id,
            "name": self.item.name,
            "description": self.item.description,
            "best_bid": {
                "id": self.best_bid.id,
                "user": self.best_bid.user.username,
                "item": self.best_bid.item.id,
                "amount": "1.00",
                "date_created": "1975-01-02T00:00:00Z",
                "last_updated": "1975-01-02T00:00:00Z",
            },
        }

    def test_serializes_model_with_best_bid(self):
        serializer_data = ItemSerializer(self.item).data
        self.assertDictEqual(serializer_data, self.expected)

    def test_serializes_model_without_best_bid(self):
        self.item.best_bid = None
        self.item.save()
        self.expected["best_bid"] = None
        serializer_data = ItemSerializer(self.item).data
        self.assertDictEqual(serializer_data, self.expected)


@freeze_time("1975-01-02T00:00:00Z")
class BidSerializerTestCase(TestCase):
    builder = Builder()

    def setUp(self) -> None:
        self.user = self.builder.user()
        self.item = self.builder.item()
        self.bid = self.builder.bid(item=self.item, user=self.user, amount=Decimal(1))

        self.expected = {
            "id": self.bid.id,
            "user": self.user.username,
            "item": self.item.id,
            "amount": "1.00",
            "date_created": "1975-01-02T00:00:00Z",
            "last_updated": "1975-01-02T00:00:00Z",
        }

    def test_serializes_bid(self):
        serializer_data = BidSerializer(self.bid).data
        self.assertDictEqual(serializer_data, self.expected)
