from decimal import Decimal
from unittest import mock

from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase

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

    def test_get_list_filtered(self):
        response = self.client.get(self.url, {"q": "0"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


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

    def test_user_cant_create_two_bids(self):
        self.client.post(self.url, self.request_data)
        self.request_data["amount"] = Decimal(2)
        response = self.client.post(self.url, self.request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        bid = Bid.objects.filter(item=self.item, user=self.user).first()
        self.assertEqual(bid.amount, Decimal(1))

    def test_user_cant_create_lower_bid(self):
        self.builder.bid(user=self.user, item=self.item, amount=Decimal(2))
        response = self.client.post(self.url, self.request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_another_user_can_create_bid(self):
        self.builder.bid(item=self.item, user=self.user, amount=Decimal(1))
        new_user = self.builder.user("new_user")
        self.client.force_authenticate(new_user)
        self.request_data["amount"] = Decimal(2)
        response = self.client.post(self.url, self.request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bid = Bid.objects.filter(item=self.item, user=new_user).first()
        self.assertEqual(bid.amount, Decimal(2))
        self.item.refresh_from_db()
        self.assertEqual(bid.pk, self.item.best_bid.pk)


@freeze_time("1975-01-02T00:00:00Z")
class BidViewSetDetailTestCase(APITransactionTestCase):
    builder = Builder()

    def setUp(self):
        self.user = self.builder.user()
        self.item = self.builder.item()
        self.bid = self.builder.bid(item=self.item, user=self.user, amount=1)
        self.client.force_authenticate(self.user)

    def test_user_can_update_to_higher_amount(self):
        url = reverse("bid-detail", kwargs={"pk": self.bid.pk})
        response = self.client.patch(url, {"amount": Decimal(2)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bid = Bid.objects.filter(item=self.item, user=self.user).first()
        self.assertEqual(bid.amount, Decimal(2))

    def test_user_cant_update_to_lower_amount(self):
        url = reverse("bid-detail", kwargs={"pk": self.bid.pk})
        response = self.client.patch(url, {"amount": Decimal(0)})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cant_see_other_user_bids(self):
        self.client.force_authenticate(self.builder.user("another"))
        url = reverse("bid-detail", kwargs={"pk": self.bid.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
