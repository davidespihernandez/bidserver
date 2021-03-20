from rest_framework.viewsets import ModelViewSet

from bids.models import Bid, Item
from bids.serializers import BidSerializer, ItemSerializer


class BidViewSet(ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.select_related("best_bid").all()
    serializer_class = ItemSerializer
