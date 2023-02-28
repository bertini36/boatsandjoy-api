from abc import ABC, abstractmethod
from decimal import Decimal

import stripe
from django.conf import settings


class PaymentGateway(ABC):
    @classmethod
    @abstractmethod
    def generate_checkout_session_id(
        cls,
        name: str,
        description: str,
        price: float,
    ) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_session_id_from_event(cls, event: dict) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_customer_email_from_event(cls, event: dict) -> str:
        pass


class StripePaymentGateway(PaymentGateway):
    @classmethod
    def generate_checkout_session_id(
        cls, name: str, description: str, price: Decimal
    ) -> str:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "name": name,
                    "description": description,
                    "amount": cls._format_price(price),
                    "currency": "eur",
                    "quantity": 1,
                }
            ],
            success_url=(
                settings.STRIPE_REDIRECT_URL + "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=settings.STRIPE_REDIRECT_URL,
        )
        return session.id

    @classmethod
    def get_session_id_from_event(cls, event: dict) -> str:
        return event["data"]["object"]["id"]

    @classmethod
    def get_customer_email_from_event(cls, event: dict) -> str:
        customer_id = event["data"]["object"]["customer"]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = stripe.Customer.retrieve(customer_id)
        return customer["email"]

    @staticmethod
    def _format_price(price):
        return int(float(price) * 100)
