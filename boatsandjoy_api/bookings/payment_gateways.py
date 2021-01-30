from abc import ABC, abstractmethod
from decimal import Decimal

import stripe
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .exceptions import PaymentGatewayException


class PaymentGateway(ABC):

    @classmethod
    @abstractmethod
    def generate_checkout_session_id(
        cls,
        name: str,
        description: str,
        photo_url: str,
        price: float,
    ) -> str:
        pass

    @classmethod
    @abstractmethod
    def register_event(cls, headers: dict, body: dict) -> dict:
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
        cls,
        name: str,
        description: str,
        photo_url: str,
        price: Decimal
    ) -> str:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        success_url = f'{settings.DOMAIN}/payment/success/'
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'name': name,
                'description': description,
                'images': [f'{photo_url}'],
                'amount': cls._format_price(price),
                'currency': 'eur',
                'quantity': 1,
            }],
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=f'{settings.DOMAIN}/payment/error/'
        )
        return session.id

    @classmethod
    def register_event(cls, headers: dict, body: dict) -> dict:
        try:
            event = stripe.Webhook.construct_event(
                body,
                headers['HTTP_STRIPE_SIGNATURE'],
                settings.STRIPE_ENDPOINT_SECRET
            )
        except ValueError as e:
            raise PaymentGatewayException(_(
                f'There has been some error in the '
                f'construction of the event: {e}'
            ))
        except stripe.error.SignatureVerificationError as e:
            raise PaymentGatewayException(
                _(f'Signature verification has failed: {e}')
            )
        return event

    @classmethod
    def get_session_id_from_event(cls, event: dict) -> str:
        return event['data']['object']['id']

    @classmethod
    def get_customer_email_from_event(cls, event: dict) -> str:
        customer_id = event['data']['object']['customer']
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = stripe.Customer.retrieve(customer_id)
        return customer['email']

    @staticmethod
    def _format_price(price):
        return int(float(price) * 100)
