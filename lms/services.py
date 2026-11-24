import uuid
from django.conf import settings

def create_stripe_product(name, description=""):
    return {"id": f"prod_{uuid.uuid4().hex[:14]}", "name": name}

def create_stripe_price(product_id, amount_in_rubles):
    return {"id": f"price_{uuid.uuid4().hex[:14]}", "unit_amount": int(amount_in_rubles * 100)}

def create_stripe_checkout_session(price_id, success_url, cancel_url):
    fake_session_id = f"cs_test_{uuid.uuid4().hex[:14]}"
    fake_url = f"https://checkout.stripe.com/c/pay/{fake_session_id}"
    return {"id": fake_session_id, "url": fake_url}