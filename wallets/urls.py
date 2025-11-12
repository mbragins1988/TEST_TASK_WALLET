from django.urls import path, include
from rest_framework.routers import DefaultRouter
from wallets.views import WalletViewSet

router = DefaultRouter()
router.register('wallets', WalletViewSet, basename='wallet')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
