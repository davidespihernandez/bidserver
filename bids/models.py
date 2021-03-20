from django.conf import settings
from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=255)
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
        unique_together = [["user", "item"], ["item", "amount"]]
        ordering = ["-amount", "-last_updated", "-pk"]
