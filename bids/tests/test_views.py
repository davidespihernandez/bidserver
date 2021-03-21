from decimal import Decimal
from unittest import mock

from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from bids.models import Bid
from bids.tests.builder import Builder


@freeze_time("1975-01-02T00:00:00Z")
class ItemViewSetListTestCase(APITestCase):
    builder = Builder()
    url = reverse("item-list")

    def setUp(self):
        self.regular_user = self.builder.user(
            username="regular_user", password="regular_user"
        )
        self.items = [
            self.builder.item(name=f"item_{i}", description=f"description_{i}")
            for i in range(2)
        ]
        self.expected = {
            "count": 2,
            "next": mock.ANY,
            "previous": mock.ANY,
            "results": [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "best_bid": None,
                }
                for item in self.items
            ],
        }
        self.client.force_authenticate(self.regular_user)

    def test_get_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, self.expected)


@freeze_time("1975-01-02T00:00:00Z")
class ItemViewSetDetailTestCase(APITestCase):
    builder = Builder()

    def setUp(self):
        self.maxDiff = None
        self.regular_user = self.builder.user(
            username="regular_user", password="regular_user"
        )
        self.admin_user = self.builder.user(
            username="admin_user", password="admin_user", is_staff=True
        )
        self.item = self.builder.item()
        self.builder.bid(item=self.item, user=self.regular_user, amount=1)
        self.best_bid = self.builder.bid(item=self.item, user=self.admin_user, amount=2)
        self.client.force_authenticate(self.regular_user)

    def test_get_detail(self):
        url = reverse("item-detail", kwargs={"pk": self.item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "id": self.item.pk,
                "name": self.item.name,
                "description": self.item.description,
                "best_bid": {
                    "id": self.best_bid.pk,
                    "user": {
                        "id": self.admin_user.pk,
                        "username": self.admin_user.username,
                    },
                    "amount": "2.00",
                    "date_created": "1975-01-02T00:00:00Z",
                    "last_updated": "1975-01-02T00:00:00Z",
                },
            },
        )

    def test_get_item_bids_regular_user(self):
        url = reverse("item-bids", kwargs={"pk": self.item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_get_item_bids_admin_user(self):
        self.client.force_authenticate(self.admin_user)
        url = reverse("item-bids", kwargs={"pk": self.item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)


@freeze_time("1975-01-02T00:00:00Z")
class BidViewSetListTestCase(APITestCase):
    builder = Builder()
    url = reverse("bid-list")

    def setUp(self):
        self.regular_user = self.builder.user(
            username="regular_user", password="regular_user"
        )
        self.admin_user = self.builder.user(
            username="admin_user", password="admin_user", is_staff=True
        )
        self.item = self.builder.item()
        self.builder.bid(item=self.item, user=self.regular_user, amount=1)
        self.best_bid = self.builder.bid(item=self.item, user=self.admin_user, amount=2)
        self.client.force_authenticate(self.regular_user)

    def test_get_list_regular_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_get_list_admin_user(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)


@freeze_time("1975-01-02T00:00:00Z")
class BidViewSetCreateTestCase(APITestCase):
    builder = Builder()
    url = reverse("bid-list")

    def setUp(self):
        self.user = self.builder.user()
        self.item = self.builder.item()
        self.client.force_authenticate(self.user)
        self.request_data = {
            "item": self.item.pk,
            "amount": Decimal(1),
        }

    def test_create_bid(self):
        response = self.client.post(self.url, self.request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bid = Bid.objects.filter(item=self.item, user=self.user).first()
        self.assertEqual(bid.amount, Decimal(1))

    def test_user_cant_create_2_bids(self):
        self.client.post(self.url, self.request_data)
        self.request_data["amount"] = Decimal(2)
        response = self.client.post(self.url, self.request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        bid = Bid.objects.filter(item=self.item, user=self.user).first()
        self.assertEqual(bid.amount, Decimal(1))