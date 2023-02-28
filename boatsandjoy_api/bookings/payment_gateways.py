from decimal import Decimal

import stripe


class StripePaymentGateway:
    def __init__(self, api_key: str, redirect_url: str):
        self.api_key = api_key
        self.redirect_url = redirect_url

    def checkout(self, name: str, description: str, price: Decimal) -> str:
        stripe.api_key = self.api_key
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "name": name,
                    "description": description,
                    "amount": self._format_price(price),
                    "currency": "eur",
                    "quantity": 1,
                }
            ],
            success_url=self.redirect_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=self.redirect_url,
        )
        return session.id

    @staticmethod
    def get_session_id_from_event(event: dict) -> str:
        return event["data"]["object"]["id"]

    def get_customer_email_from_event(self, event: dict) -> str:
        customer_id = event["data"]["object"]["customer"]
        stripe.api_key = self.api_key
        customer = stripe.Customer.retrieve(customer_id)
        return customer["email"]

    @staticmethod
    def _format_price(price):
        return int(float(price) * 100)
