
# Create your tests here.
from django.test import TestCase
from audit.models import Tenant, InferenceRecord, create_inference_record, verify_chain


class HashChainIntegrityTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            api_key_id="test-key",
            hmac_secret_hash="test-secret",
        )

    def test_clean_chain_verifies(self):
        create_inference_record(
            tenant=self.tenant, user_ref="u1", model_version="gpt-4o-mini",
            provider="openai", input_payload={"a": 1}, output_payload={"b": 2},
            latency_ms=100, cost_usd=0.0021,
        )
        create_inference_record(
            tenant=self.tenant, user_ref="u2", model_version="gpt-4o-mini",
            provider="openai", input_payload={"a": 3}, output_payload={"b": 4},
            latency_ms=150, cost_usd=1.5,
        )
        self.assertTrue(verify_chain(self.tenant))

    def test_tampering_is_detected(self):
        record = create_inference_record(
            tenant=self.tenant, user_ref="u1", model_version="gpt-4o-mini",
            provider="openai", input_payload={"a": 1}, output_payload={"b": 2},
            latency_ms=100,
        )
        self.assertTrue(verify_chain(self.tenant))

        record.output_payload = {"b": "TAMPERED"}
        record.save()

        self.assertFalse(verify_chain(self.tenant))

    def test_cost_usd_canonicalisation_is_stable(self):
        """Regression test for the float-vs-Decimal hashing bug found 2026-10-04."""
        create_inference_record(
            tenant=self.tenant, user_ref="u1", model_version="gpt-4o-mini",
            provider="openai", input_payload={"a": 1}, output_payload={"b": 2},
            latency_ms=100, cost_usd=0.0021,
        )
        self.assertTrue(verify_chain(self.tenant))