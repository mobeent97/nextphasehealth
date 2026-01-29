from django.urls import path
from .views import GHLWebhookView

urlpatterns = [
    path('ghl-webhook/', GHLWebhookView.as_view(), name='ghl-webhook'),
]
