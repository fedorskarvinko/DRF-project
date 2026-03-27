from rest_framework import serializers

from .models import User, Payment
from materials.serializers import CourseSerializer, LessonSerializer


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    course_title = serializers.ReadOnlyField(source='paid_course.title', default=None)
    lesson_title = serializers.ReadOnlyField(source='paid_lesson.title', default=None)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_email', 'payment_date', 'paid_course', 'paid_lesson',
                  'course_title', 'lesson_title', 'amount', 'payment_method']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "city", "avatar"]
        read_only_fields = ["id"]


class UserDetailSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar',
                  'payments', 'total_spent']
        read_only_fields = ['id', 'email']

    def get_total_spent(self, obj):
        return sum(payment.amount for payment in obj.payments.all())
