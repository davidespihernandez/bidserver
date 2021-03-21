from django.conf import settings
from django.db import models

from bids.exceptions import (
    HigherBidAlreadyExists,
    UserAlreadyHasABid,
    LowerAmountNotAllowed,
)


class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    best_bid = models.OneToOneField(
        "Bid", on_delete=models.SET_NULL, null=True, related_name="best_item"
    )


class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["user", "item"]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_amount = self.amount

    def user_has_another_bid(self):
        """
        Returns whether the user already has a bid for the bid item.
        :return: boolean
        """
        return (
            Bid.objects.filter(item=self.item, user=self.user)
            .exclude(pk=self.pk)
            .exists()
        )

    def save(self, *args, **kwargs):
        current_best_bid = self.item.best_bid
        if self.amount < self._previous_amount:
            raise LowerAmountNotAllowed(
                f"Trying to lower amount from {self._previous_amount} to {self.amount}"
            )

        if current_best_bid and current_best_bid.amount > self.amount:
            raise HigherBidAlreadyExists(
                f"A bid higher than {self.amount} already exists"
            )
        if self.user_has_another_bid():
            raise UserAlreadyHasABid("The user already has a bid for this item")

        super().save(*args, **kwargs)
        self._previous_amount = self.amount
        self.item.best_bid = self
        self.item.save()
