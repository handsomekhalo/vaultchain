import hmac, hashlib, time

def sign_request(secret: str, method: str, path: str, body: str, timestamp: str) -> str:
    message = f"{method}\n{path}\n{body}\n{timestamp}"
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()