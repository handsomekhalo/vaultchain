# audit/api/views.py
import hmac
from urllib import request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from audit.models import Tenant, InferenceRecord, create_inference_record
from tenants.management.commands.sign_request import sign_request
from .serializers import InferenceRecordCreateSerializer, InferenceRecordReadSerializer
import time


# def _authenticate(request):
#     api_key = request.headers.get("X-Api-Key")
#     return Tenant.objects.filter(api_key_id=api_key).first()
def _authenticate(request):
    print("HEADERS RECEIVED:", dict(request.headers))  # TEMP debug — remove after this works

    api_key = request.headers.get("X-Api-Key")
    timestamp = request.headers.get("X-Timestamp")
    signature = request.headers.get("X-Signature")

    if not api_key or not timestamp or not signature:
        return None

    tenant = Tenant.objects.filter(api_key_id=api_key).first()
    if not tenant:
        return None

    try:
        if abs(time.time() - float(timestamp)) > 300:
            return None
    except ValueError:
        return None

    expected = sign_request(tenant.hmac_secret_hash, request.method, request.path, request.body.decode(), timestamp)
    print("EXPECTED:", expected)
    print("RECEIVED:", signature)
    print("SIGNED PATH:", request.path)
    if not hmac.compare_digest(expected, signature):
        return None

    return tenant

@api_view(["POST"])
def create_inference_api(request):
    tenant = _authenticate(request)
    if not tenant:
        return Response({"error": "invalid api key"}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = InferenceRecordCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    record = create_inference_record(tenant=tenant, **serializer.validated_data)
    return Response(InferenceRecordReadSerializer(record).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_inference_api(request, record_id):
    tenant = _authenticate(request)
    if not tenant:
        return Response({"error": "invalid api key"}, status=status.HTTP_401_UNAUTHORIZED)

    record = InferenceRecord.objects.filter(id=record_id, tenant=tenant).first()
    if not record:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(InferenceRecordReadSerializer(record).data)