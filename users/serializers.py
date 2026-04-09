from rest_framework import serializers

from materials.serializers import CourseSerializer, LessonSerializer

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    course_title = serializers.ReadOnlyField(source="paid_course.title", default=None)
    lesson_title = serializers.ReadOnlyField(source="paid_lesson.title", default=None)

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
        ]

        read_only_fields = ["id", "payment_date"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "city", "avatar"]
        read_only_fields = ["id"]


class UserDetailSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField()
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
            # Только для своего профиля показываем платежи
            request = self.context.get("request")
            if request and request.user == obj:
                from .serializers import PaymentSerializer

                payments = obj.payments.all()
                return PaymentSerializer(payments, many=True).data
            return []

    def get_total_spent(self, obj):
        # Только для своего профиля показываем сумму
        request = self.context.get("request")
        if request and request.user == obj:
            return sum(payment.amount for payment in obj.payments.all())
        return 0

class UserPublicSerializer(serializers.ModelSerializer):
        """
        Сериализатор для публичного просмотра профилей
        """

        class Meta:
            model = User
            fields = ["id", "email", "first_name", "city", "avatar"]
            read_only_fields = ["id", "email", "first_name", "city", "avatar"]

class PaymentSerializer(serializers.ModelSerializer):
        user_email = serializers.ReadOnlyField(source="user.email")
        course_title = serializers.ReadOnlyField(
            source="paid_course.title", default=None
        )
        lesson_title = serializers.ReadOnlyField(
            source="paid_lesson.title", default=None
        )

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
            ]
            read_only_fields = ["id", "payment_date"]

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
