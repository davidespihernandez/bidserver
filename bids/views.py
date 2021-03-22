from django.db.models import Q
from django_filters import rest_framework as filters
from django.db import transaction
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet

from bids.models import Bid, Item
from bids.serializers import (
    BidDetailSerializer,
    ItemDetailSerializer,
    BidCreateSerializer,
    BidUpdateSerializer,
)


class BidViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    Bids.
    POST: create a new bid for a user-item
    PATCH: update an existing bid
    GET: retrieve the list or detail of a bid
    Admin users can access all bids, the rest of users are limited to their own bids.
    """

    queryset = Bid.objects.select_related("item", "user").order_by("date_created", "pk")
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


class ItemFilter(filters.FilterSet):
    q = filters.CharFilter(method="filter_text")

    def filter_text(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )


class ItemViewSet(ReadOnlyModelViewSet):
    """
    Items.
    GET: Retrieves the list or detail of an item, including the best bid so far.
    """

    queryset = Item.objects.select_related("best_bid").order_by("name")
    serializer_class = ItemDetailSerializer
    filterset_class = ItemFilter

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
