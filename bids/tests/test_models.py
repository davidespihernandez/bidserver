from decimal import Decimal

from django.test import TestCase

from bids.exceptions import (
    HigherBidAlreadyExists,
    UserAlreadyHasABid,
    LowerAmountNotAllowed,
)
from bids.models import Bid
from bids.tests.builder import Builder


class BidModelTestCase(TestCase):
    builder = Builder()

    def setUp(self) -> None:
        self.item = self.builder.item("biditem")
        self.user = self.builder.user("biduser")

    def test_save_bid(self):
        """
        Given an item without best_bid
        when we save a bid,
        then that bid becomes the best_bid
        """
        bid = Bid(item=self.item, user=self.user, amount=Decimal(1))
        bid.save()
        self.item.refresh_from_db()
        self.assertEqual(self.item.best_bid.pk, bid.pk)

    def test_save_bid_less_amount_fails_for_same_user(self):
        """
        Given an existing bid on an item
        when we save a bid with less amount for the same user
        then an exception is thrown
        """
        Bid(item=self.item, user=self.user, amount=Decimal(2)).save()
        with self.assertRaises(HigherBidAlreadyExists):
            Bid(item=self.item, user=self.user, amount=Decimal(1)).save()

    def test_save_bid_less_amount_fails_for_another_user(self):
        """
        Given an existing bid on an item
        when we save a bid with less amount for another user
        then an exception is thrown
        """
        Bid(item=self.item, user=self.user, amount=Decimal(2)).save()
        with self.assertRaises(HigherBidAlreadyExists):
            Bid(
                item=self.item, user=self.builder.user("newuser"), amount=Decimal(1)
            ).save()

    def test_user_can_only_have_a_bid_per_item(self):
        """
        Given an existing bid on an item
        when we try to save a new bid for the same user and the same item
        then an exception is thrown
        """
        Bid(item=self.item, user=self.user, amount=Decimal(1)).save()
        with self.assertRaises(UserAlreadyHasABid):
            Bid(item=self.item, user=self.user, amount=Decimal(2)).save()

    def test_user_can_have_bids_on_several_items(self):
        """
        Given an existing bid on an item
        when we save a new bid for the same user and another item
        then the user will have 2 bids
        """
        Bid(item=self.item, user=self.user, amount=Decimal(2)).save()
        Bid(item=self.builder.item("newitem"), user=self.user, amount=Decimal(2)).save()
        self.assertEqual(Bid.objects.filter(user=self.user).count(), 2)

    def test_bid_can_be_updated_to_a_higher_amount(self):
        """
        Given an existing bid on an item
        when we update that bid to a higher amount
        then the bid is properly updated
        """
        bid = Bid(item=self.item, user=self.user, amount=Decimal(2))
        bid.save()
        bid.amount = Decimal(3)
        bid.save()
        bid.refresh_from_db()
        self.assertEqual(bid.amount, Decimal(3))

    def test_bid_updated_to_lower_amount_fails(self):
        """
        Given an existing bid on an item
        when we update that bid to a lower amount
        then an exception is raised
        """
        bid = Bid(item=self.item, user=self.user, amount=2)
        bid.save()
        with self.assertRaises(LowerAmountNotAllowed):
            bid.amount = Decimal(1)
            bid.save()
