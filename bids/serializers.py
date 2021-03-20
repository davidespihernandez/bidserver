from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from bids.models import Item, Bid


class BidSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username")

    def validate_user(self, username):
        return get_object_or_404(get_user_model(), username=username)

    class Meta:
        model = Bid
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    best_bid = BidSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "description", "best_bid"]
