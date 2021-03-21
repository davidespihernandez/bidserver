from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from bids.models import Bid, Item
from bids.serializers import (
    BidDetailSerializer,
    ItemDetailSerializer,
    BidCreateSerializer,
    BidUpdateSerializer,
)


class BidViewSet(ModelViewSet):
    queryset = Bid.objects.all().order_by("date_created", "pk")
    serializer_class = BidDetailSerializer

    def get_serializer_class(self, *args, **kwargs):
        method = self.request.method
        if method == "GET":
            return BidDetailSerializer
        elif method == "PATCH":
            return BidUpdateSerializer
        elif method == "POST":
            return BidCreateSerializer
        else:
            raise MethodNotAllowed(method)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)


class ItemViewSet(ReadOnlyModelViewSet):
    queryset = Item.objects.select_related("best_bid").order_by("name")
    serializer_class = ItemDetailSerializer

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def bids(self, request, pk=None):
        bids = Bid.objects.select_related("user", "item").filter(item_id=pk)
        user = request.user
        if not user.is_staff:
            bids = bids.filter(user=user)

        page = self.paginate_queryset(bids)
        if page is not None:
            serializer = BidDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BidDetailSerializer(bids, many=True)
        return Response(serializer.data)
