import hashlib
import hmac

secret_key = "bpsr13Dieu@#@!$%&*()_+"

def generate_signature(data: str) -> str:
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

def compare_signature(sig1: str, sig2 : str):
    return hmac.compare_digest(sig1,sig2)