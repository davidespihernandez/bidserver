from rest_framework.exceptions import ValidationError


class BidException(ValidationError):
    """Generic bid exception"""


class HigherBidAlreadyExists(BidException):
    """
    Raised when trying to save a bid but the item
    already has a higher bid
    """


class UserAlreadyHasABid(BidException):
    """
    Raised when trying to create a new bid for an item but
    the user already has a bid for that item. Instead of
    creating a new one, the existing should be updated.
    """


class LowerAmountNotAllowed(BidException):
    """
    Raised when trying to update a bid to a lower amount.
    """
