from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from materials.models import Course
from users.serializers import (
    PaymentSerializer,
    UserDetailSerializer,
    UserPublicSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    SubscriptionSerializer,
    PaymentCreateSerializer,
)

from .models import Payment, User, Subscription
from .permissions import IsOwner
from .services import StripeService


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        elif self.action == "retrieve":
            # Для просмотра чужого профиля используем публичный сериализатор
            user = self.get_object()
            if self.request.user == user:
                return UserDetailSerializer
            return UserPublicSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            # Регистрация доступна всем
            permission_classes = [AllowAny]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Редактирование и удаление только для владельца
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр списка и деталей для авторизованных
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Получение своего профиля"""
        serializer = UserDetailSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Пользователи видят только свои платежи
        return Payment.objects.filter(user=self.request.user)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления подписками
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(f"Getting subscriptions for user: {self.request.user.id}")
        qs = Subscription.objects.filter(user=self.request.user)
        print(f"Found {qs.count()} subscriptions")
        return qs

    def list(self, request, *args, **kwargs):
        print("LIST method called")
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def toggle(self, request):
        """
        Переключение подписки на курс
        """
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Не указан ID курса"}, status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(user=request.user, course=course)

        if subscription.exists():
            subscription.delete()
            return Response(
                {"message": "Подписка удалена", "is_subscribed": False},
                status=status.HTTP_200_OK,
            )
        else:
            Subscription.objects.create(user=request.user, course=course)
            return Response(
                {"message": "Подписка добавлена", "is_subscribed": True},
                status=status.HTTP_201_CREATED,
            )


class PaymentCreateView(generics.CreateAPIView):
    """
    Создание платежа с интеграцией Stripe
    """

    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        # Получаем название и описание продукта
        if payment.paid_course:
            product_name = payment.paid_course.title
            product_description = payment.paid_course.description
        else:
            product_name = payment.paid_lesson.title
            product_description = payment.paid_lesson.description

        # Создаем продукт в Stripe
        stripe_product = StripeService.create_product(
            name=product_name, description=product_description
        )
        payment.stripe_product_id = stripe_product.id

        # Создаем цену в Stripe
        stripe_price = StripeService.create_price(
            product_id=stripe_product.id, amount=payment.amount
        )
        payment.stripe_price_id = stripe_price.id

        # Создаем сессию оплаты
        success_url = f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{settings.FRONTEND_URL}/payment/cancel"

        stripe_session = StripeService.create_checkout_session(
            price_id=stripe_price.id,
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=payment.id,
        )

        payment.stripe_session_id = stripe_session.id
        payment.payment_url = stripe_session.url
        payment.save()


class PaymentStatusView(generics.RetrieveAPIView):
    """
    Проверка статуса платежа
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()

        # Получаем актуальный статус из Stripe
        if payment.stripe_session_id:
            session = StripeService.retrieve_session(payment.stripe_session_id)
            payment.payment_status = session.payment_status
            payment.save()

        return super().retrieve(request, *args, **kwargs)
