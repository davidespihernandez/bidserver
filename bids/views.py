from django.db import transaction
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from bids.models import Bid, Item
from bids.serializers import BidSerializer, ItemSerializer


class BidViewSet(ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ItemViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Item.objects.select_related("best_bid").all()
    serializer_class = ItemSerializer

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def bids(self, request, pk=None):
        item = get_object_or_404(Item, pk=pk)
        bids = Bid.objects.select_related("user", "item").filter(
            item=item, user=request.user
        )

        page = self.paginate_queryset(bids)
        if page is not None:
            serializer = BidSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BidSerializer(bids, many=True)
        return Response(serializer.data)
