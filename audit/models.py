from django.db import models
from decimal import Decimal

# Create your models here.
"""
VaultChain — audit app models
First task: schema + hash chain. Everything else (storage nodes, SDK,
S3-compatible endpoints) writes into this.

Setup:
    python manage.py startapp audit   # if you haven't already
    # drop this file in audit/models.py
    # add "audit" to INSTALLED_APPS
    python manage.py makemigrations audit
    python manage.py migrate
"""

import hashlib
import json
import uuid

from django.conf import settings
from django.db import models


class Tenant(models.Model):
    """A firm/company using VaultChain. Mirrors the 'firm' pattern from ClearWave."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    api_key_id = models.CharField(max_length=64, unique=True, db_index=True)
    # HMAC signing secret for this tenant's presigned write tokens.
    # Store hashed, never plaintext, same as you'd treat a password.
    hmac_secret_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class InferenceRecord(models.Model):
    """
    One AI inference audit record. Append-only: the model intentionally
    has no update path exposed at the API layer — only create + read.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, related_name="inference_records")
    user_ref = models.CharField(max_length=255, help_text="Tenant's own user identifier, not a VaultChain user")

    # AI-native fields
    model_version = models.CharField(max_length=255)
    provider = models.CharField(max_length=100)  # e.g. "openai", "anthropic", "self-hosted"
    input_payload = models.JSONField()
    output_payload = models.JSONField()
    latency_ms = models.PositiveIntegerField()
    token_count = models.PositiveIntegerField(null=True, blank=True)
    cost_usd = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)

    

    # Hash chain — the tamper-evidence layer
    prev_hash = models.CharField(max_length=64, db_index=True)
    record_hash = models.CharField(max_length=64, unique=True, db_index=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["tenant", "timestamp"]),
            models.Index(fields=["tenant", "model_version"]),
        ]

    def __str__(self):
        return f"{self.tenant_id}:{self.id}"



def _normalize_cost(cost_usd):
    if cost_usd is None:
        return None
    return str(Decimal(str(cost_usd)).quantize(Decimal("0.000001")))

def compute_record_hash(prev_hash: str, payload: dict) -> str:
    """
    hash = SHA256(prev_hash + canonical_json(payload))

    Canonical JSON (sorted keys, no whitespace variance) so the same
    logical payload always hashes the same way regardless of dict
    ordering. This is what makes the chain independently verifiable
    by a third party — anyone can recompute it from raw fields.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256((prev_hash + canonical).encode("utf-8")).hexdigest()


def get_last_hash(tenant: Tenant) -> str:
    """
    Genesis hash for a tenant's chain is 64 zeros. Every subsequent
    record chains off the previous record's hash, scoped per tenant
    (each tenant has its own independent chain, not one global chain —
    this matches the multi-tenant isolation requirement and avoids
    cross-tenant chain contention).
    """
    last = (
        InferenceRecord.objects.filter(tenant=tenant)
        .order_by("-timestamp")
        .values_list("record_hash", flat=True)
        .first()
    )
    return last or "0" * 64


def create_inference_record(*, tenant: Tenant, user_ref: str, model_version: str,
                             provider: str, input_payload: dict, output_payload: dict,
                             latency_ms: int, token_count: int | None = None,
                             cost_usd: float | None = None) -> InferenceRecord:
    """
    The only way a record should be created. Wrapping this in a single
    function (rather than letting callers build InferenceRecord() directly)
    means the hash chain can never be computed inconsistently or skipped.
    """
    prev_hash = get_last_hash(tenant)

    payload_for_hash = {
        "tenant_id": str(tenant.id),
        "user_ref": user_ref,
        "model_version": model_version,
        "provider": provider,
        "input_payload": input_payload,
        "output_payload": output_payload,
        "latency_ms": latency_ms,
        "token_count": token_count,
        # "cost_usd": str(cost_usd) if cost_usd is not None else None,
        "cost_usd": _normalize_cost(cost_usd),
    }
    record_hash = compute_record_hash(prev_hash, payload_for_hash)

    return InferenceRecord.objects.create(
        tenant=tenant,
        user_ref=user_ref,
        model_version=model_version,
        provider=provider,
        input_payload=input_payload,
        output_payload=output_payload,
        latency_ms=latency_ms,
        token_count=token_count,
        cost_usd=cost_usd,
        prev_hash=prev_hash,
        record_hash=record_hash,
    )


def verify_chain(tenant: Tenant) -> bool:
    """
    Walks the tenant's full chain and recomputes every hash from raw
    fields. Returns False the moment a mismatch is found — that's your
    tamper-evidence check, and it's the function your regulator export
    and DSAR tooling in Sprint 3 will call.
    """
    records = InferenceRecord.objects.filter(tenant=tenant).order_by("timestamp")
    expected_prev = "0" * 64

    for record in records:
        if record.prev_hash != expected_prev:
            return False
        payload_for_hash = {
            "tenant_id": str(record.tenant_id),
            "user_ref": record.user_ref,
            "model_version": record.model_version,
            "provider": record.provider,
            "input_payload": record.input_payload,
            "output_payload": record.output_payload,
            "latency_ms": record.latency_ms,
            "token_count": record.token_count,
            # "cost_usd": str(record.cost_usd) if record.cost_usd is not None else None,
            "cost_usd": _normalize_cost(record.cost_usd),
        }
        recomputed = compute_record_hash(expected_prev, payload_for_hash)
        if recomputed != record.record_hash:
            return False
        expected_prev = record.record_hash

    return True