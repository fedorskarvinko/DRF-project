from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .apps import UsersConfig
from .views import PaymentListView, UserViewSet, SubscriptionViewSet

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("", include(router.urls)),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
]
