"""
Сервисные функции для работы с Stripe API
"""
import stripe
from django.conf import settings
from decimal import Decimal

# Настройка Stripe API ключа
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name: str, description: str = None) -> dict:
    """
    Создает продукт в Stripe
    
    Args:
        name: Название продукта
        description: Описание продукта (опционально)
    
    Returns:
        dict: Данные созданного продукта
    """
    try:
        product_data = {
            'name': name,
        }
        if description:
            product_data['description'] = description
        
        product = stripe.Product.create(**product_data)
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании продукта в Stripe: {str(e)}")


def create_stripe_price(product_id: str, amount: Decimal, currency: str = 'rub') -> dict:
    """
    Создает цену для продукта в Stripe
    
    Args:
        product_id: ID продукта в Stripe
        amount: Сумма в рублях
        currency: Валюта (по умолчанию 'rub')
    
    Returns:
        dict: Данные созданной цены
    """
    try:
        # Конвертируем рубли в копейки для Stripe
        amount_in_cents = int(float(amount) * 100)
        
        price = stripe.Price.create(
            unit_amount=amount_in_cents,
            currency=currency,
            product=product_id,
        )
        return {
            'id': price.id,
            'amount': price.unit_amount,
            'currency': price.currency,
            'product_id': price.product,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании цены в Stripe: {str(e)}")


def create_stripe_checkout_session(price_id: str, success_url: str, cancel_url: str) -> dict:
    """
    Создает сессию для оплаты в Stripe
    
    Args:
        price_id: ID цены в Stripe
        success_url: URL для перенаправления после успешной оплаты
        cancel_url: URL для перенаправления при отмене оплаты
    
    Returns:
        dict: Данные созданной сессии
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return {
            'id': session.id,
            'url': session.url,
            'payment_status': session.payment_status,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании сессии оплаты в Stripe: {str(e)}")


def retrieve_stripe_session(session_id: str) -> dict:
    """
    Получает информацию о сессии оплаты в Stripe
    
    Args:
        session_id: ID сессии в Stripe
    
    Returns:
        dict: Данные сессии
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'id': session.id,
            'payment_status': session.payment_status,
            'payment_intent': session.payment_intent,
            'customer_email': session.customer_details.email if session.customer_details else None,
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при получении сессии из Stripe: {str(e)}")

