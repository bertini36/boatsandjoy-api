from django.conf import settings

from boatsandjoy_api.bookings.payment_gateways import StripePaymentGateway
from boatsandjoy_api.bookings.services.create_booking import CreateBookingService


def build_create_booking_service() -> CreateBookingService:
    return CreateBookingService(
        StripePaymentGateway(settings.STRIPE_SECRET_KEY, settings.STRIPE_REDIRECT_URL),
    )
