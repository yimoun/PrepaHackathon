import requests
from django.conf import settings

def verify_recaptcha(token: str) -> bool:
    secret_key = settings.RECAPTCHA_SECRET_KEY  # On lira la clé depuis les settings
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": secret_key,
            "response": token,
        },
    )
    result = response.json()
    return result.get("success", False)
