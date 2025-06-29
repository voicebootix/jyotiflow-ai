import stripe
from typing import Tuple, Optional
import os

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")

async def create_stripe_product(name: str, price: float) -> Tuple[str, str]:
    """Create Stripe product and price"""
    try:
        # Create product
        product = stripe.Product.create(
            name=name,
            description=f"JyotiFlow.ai - {name}"
        )
        
        # Create price
        price_obj = stripe.Price.create(
            product=product.id,
            unit_amount=int(price * 100),  # Convert to cents
            currency="usd"
        )
        
        return product.id, price_obj.id
    except Exception as e:
        print(f"Stripe error: {e}")
        return None, None

async def create_stripe_subscription_plan(name: str, monthly_price: float) -> Tuple[str, str]:
    """Create Stripe subscription plan"""
    try:
        # Create product
        product = stripe.Product.create(
            name=f"Subscription: {name}",
            description=f"JyotiFlow.ai Monthly Subscription - {name}"
        )
        
        # Create recurring price
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(monthly_price * 100),
            currency="usd",
            recurring={"interval": "month"}
        )
        
        return product.id, price.id
    except Exception as e:
        print(f"Stripe subscription error: {e}")
        return None, None

async def create_stripe_credit_package(name: str, price: float) -> Tuple[str, str]:
    """Create Stripe credit package"""
    try:
        # Create product
        product = stripe.Product.create(
            name=f"Credits: {name}",
            description=f"JyotiFlow.ai Credit Package - {name}"
        )
        
        # Create one-time price
        price_obj = stripe.Price.create(
            product=product.id,
            unit_amount=int(price * 100),
            currency="usd"
        )
        
        return product.id, price_obj.id
    except Exception as e:
        print(f"Stripe credit package error: {e}")
        return None, None 