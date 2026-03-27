from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, PaymentListView

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
]
