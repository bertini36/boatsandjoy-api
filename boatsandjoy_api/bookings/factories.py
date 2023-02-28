from django.conf import settings

from boatsandjoy_api.bookings.payment_gateways import StripePaymentGateway
from boatsandjoy_api.bookings.services.bookings_service import BookingsService


def build_bookings_service() -> BookingsService:
    return BookingsService(
        StripePaymentGateway(settings.STRIPE_SECRET_KEY, settings.STRIPE_REDIRECT_URL),
    )
