from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.serializers import (PaymentSerializer, UserDetailSerializer,
                               UserPublicSerializer,
                               UserRegistrationSerializer, UserSerializer)

from .models import Payment, User
from .permissions import IsOwner


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
        if self.action == 'create':
            # Регистрация доступна всем
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактирование и удаление только для владельца
            permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр списка и деталей для авторизованных
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получение своего профиля"""
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ['-payment_date']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Пользователи видят только свои платежи
        return Payment.objects.filter(user=self.request.user)
