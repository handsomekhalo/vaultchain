from rest_framework import serializers
from audit.models import InferenceRecord

class InferenceRecordCreateSerializer(serializers.Serializer):
    user_ref = serializers.CharField()
    model_version = serializers.CharField()
    provider = serializers.CharField()
    input_payload = serializers.JSONField()
    output_payload = serializers.JSONField()
    latency_ms = serializers.IntegerField()
    token_count = serializers.IntegerField(required=False, allow_null=True)
    cost_usd = serializers.DecimalField(max_digits=12, decimal_places=6, required=False, allow_null=True)

class InferenceRecordReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceRecord
        fields = "__all__"