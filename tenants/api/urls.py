# audit/api/urls.py
from django.urls import path

from tenants.api.views import verify_tenant_chain_api

urlpatterns = [
    path("verify_tenant_chain_api/", verify_tenant_chain_api, name="verify_tenant_chain_api"),
]