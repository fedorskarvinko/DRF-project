import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Сервис для работы с Stripe API
    """

    @staticmethod
    def create_product(name, description=None):
        """
        Создание продукта в Stripe
        """
        product_data = {
            "name": name,
            "type": "service",
        }
        if description:
            product_data["description"] = description

        return stripe.Product.create(**product_data)

    @staticmethod
    def create_price(product_id, amount, currency="rub"):
        """
        Создание цены для продукта
        Сумма указывается в копейках (для рубля - в копейках)
        """
        return stripe.Price.create(
            product=product_id,
            unit_amount=int(amount * 100),  # Конвертируем в копейки
            currency=currency,
        )

    @staticmethod
    def create_checkout_session(
        price_id, success_url, cancel_url, client_reference_id=None
    ):
        """
        Создание сессии оплаты
        """
        session_data = {
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            "mode": "payment",
        }

        if client_reference_id:
            session_data["client_reference_id"] = str(client_reference_id)

        return stripe.checkout.Session.create(**session_data)

    @staticmethod
    def retrieve_session(session_id):
        """
        Получение информации о сессии оплаты
        """
        return stripe.checkout.Session.retrieve(session_id)
