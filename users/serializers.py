from rest_framework import serializers

from materials.serializers import CourseSerializer

from .models import Payment, User, Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "course_title", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "city", "avatar"]
        read_only_fields = ["id"]


class UserDetailSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField()
    subscriptions = SubscriptionSerializer(many=True, read_only=True)
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "payments",
            "subscriptions",
            "total_spent",
        ]
        read_only_fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        ]

    def get_payments(self, obj):
        from .serializers import PaymentSerializer

        request = self.context.get("request")
        if request and request.user == obj:
            payments = obj.payments.all()
            return PaymentSerializer(payments, many=True).data
        return []

    def get_total_spent(self, obj):
        request = self.context.get("request")
        if request and request.user == obj:
            return sum(payment.amount for payment in obj.payments.all())
        return 0


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "city", "avatar"]
        read_only_fields = ["id", "email", "first_name", "city", "avatar"]


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    course_title = serializers.ReadOnlyField(source="paid_course.title")
    lesson_title = serializers.ReadOnlyField(source="paid_lesson.title")

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "payment_date",
            "paid_course",
            "paid_lesson",
            "course_title",
            "lesson_title",
            "amount",
            "payment_method",
            "payment_url",
            "stripe_session_id",
            "payment_status",
        ]
        read_only_fields = [
            "id",
            "payment_date",
            "payment_url",
            "stripe_session_id",
            "payment_status",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        label="Подтверждение пароля",
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone",
            "city",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'paid_course', 'paid_lesson', 'amount', 'payment_method',
                  'payment_url', 'stripe_session_id', 'payment_status']
        read_only_fields = ['id', 'payment_url', 'stripe_session_id', 'payment_status']

    def validate(self, data):
        # Проверяем, что указан либо курс, либо урок
        if not data.get('paid_course') and not data.get('paid_lesson'):
            raise serializers.ValidationError("Необходимо указать либо курс, либо урок для оплаты")
        return data