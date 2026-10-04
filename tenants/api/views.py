
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from audit.api.views import _authenticate
from audit.models import Tenant, InferenceRecord, create_inference_record, verify_chain
import hmac, hashlib, time
import secrets


# Tenant.objects.filter(name="ClearWave Test").update(
#     hmac_secret_hash=secrets.token_hex(32)  # for now, store plaintext-as-hash placeholder; proper hashing next
# )


@api_view(["GET"])
def verify_tenant_chain_api(request):
    tenant = _authenticate(request)
    if not tenant:
        return Response({"error": "invalid api key"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({"valid": verify_chain(tenant)})



#under test script
