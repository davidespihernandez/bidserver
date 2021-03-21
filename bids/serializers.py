from django.contrib.auth import get_user_model
from rest_framework import serializers

from bids.models import Item, Bid


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]


class ItemSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "description"]


class BidDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    item = ItemSimpleSerializer()

    class Meta:
        model = Bid
        fields = "__all__"


class ItemBestBidSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Bid
        fields = ["id", "user", "amount", "date_created", "last_updated"]


class BidCreateSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        return super().save(**kwargs, user=self.context["request"].user)

    class Meta:
        model = Bid
        fields = ["item", "amount"]


class BidUpdateSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        return super().save(**kwargs, user=self.context["request"].user)

    class Meta:
        model = Bid
        fields = ["amount"]


class ItemDetailSerializer(serializers.ModelSerializer):
    best_bid = ItemBestBidSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "description", "best_bid"]
