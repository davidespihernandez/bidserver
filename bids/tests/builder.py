from decimal import Decimal

from django.contrib.auth import get_user_model

from bids.models import Item, Bid


class Builder:
    def item(self, name=None, description=None) -> Item:
        item, created = Item.objects.get_or_create(
            name=name or "Item name", description=description or "Description"
        )
        return item

    def user(self, username=None, password=None):
        user_model = get_user_model()
        user = user_model(username=username or "user")
        user.set_password(password or "password")
        user.save()
        return user

    def bid(self, item=None, user=None, amount=None) -> Bid:
        bid, created = Bid.objects.get_or_create(
            item=item or self.item(),
            user=user or self.user(),
            amount=amount or Decimal(1),
        )
        return bid
