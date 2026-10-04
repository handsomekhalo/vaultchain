import hmac
import hashlib
import time
import json

SECRET = "c393a638112c48746e924749ce22a9a21daa277d3737f0adc64d094e8d9dc013"
METHOD = "POST"
# PATH = "/audit_api/create_inference_api/"   # <-- check this matches your actual urls.py path exactly
PATH = "/audit_api/create_inference_api/" 
  # match your actual urls.py exactly
body_dict = {
    "user_ref": "test-user-1",
    "model_version": "gpt-4o-mini",
    "provider": "openai",
    "input_payload": {"prompt": "summarize this contract clause"},
    "output_payload": {"result": "clause limits liability to direct damages"},
    "latency_ms": 340,
    "token_count": 128,
    "cost_usd": 0.0021,
}
body_str = json.dumps(body_dict)  # generate ONCE, use this exact string everywhere

timestamp = str(time.time())

message = f"{METHOD}\n{PATH}\n{body_str}\n{timestamp}"
signature = hmac.new(SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

print("BODY (paste exactly into Bruno's body):")
print(body_str)
print()
print("X-Timestamp header:", timestamp)
print("X-Signature header:", signature)

# import hmac, hashlib, time

# def sign_request(secret: str, method: str, path: str, body: str, timestamp: str) -> str:
#     message = f"{method}\n{path}\n{body}\n{timestamp}"
#     return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()