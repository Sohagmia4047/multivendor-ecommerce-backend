import requests
from django.conf import settings


def get_ssl_base_url():
    is_sandbox = getattr(settings, "SSLCOMMERZ_IS_SANDBOX", True)
    return "https://sandbox.sslcommerz.com" if is_sandbox else "https://securepay.sslcommerz.com"


def initiate_ssl_payment(payload: dict):
    base_url = get_ssl_base_url()
    url = f"{base_url}/gwprocess/v4/api.php"

    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def validate_ssl_payment(val_id: str):
    base_url = get_ssl_base_url()
    url = f"{base_url}/validator/api/validationserverAPI.php"

    params = {
        "val_id": val_id,
        "store_id": getattr(settings, "SSLCOMMERZ_STORE_ID", ""),
        "store_passwd": getattr(settings, "SSLCOMMERZ_STORE_PASSWORD", ""),
        "v": 1,
        "format": "json",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()