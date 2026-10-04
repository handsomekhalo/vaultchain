# audit/api/urls.py
from django.urls import path
from .views import create_inference_api, get_inference_api

urlpatterns = [
    path("create_inference_api/", create_inference_api, name="create_inference_api"),
    path("get_inference_api/<uuid:record_id>/", get_inference_api, name="get_inference_api"),
]