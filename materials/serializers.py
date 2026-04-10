from rest_framework import serializers

from materials.models import Course, Lesson
from users.models import Subscription

from .validators import YouTubeUrlValidator, validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "description",
            "preview",
            "video_link",
            "course",
            "owner",
        ]
        read_only_fields = ["owner"]
        validators = [YouTubeUrlValidator(field="video_link")]

        def validate_video_link(self, value):
            validate_youtube_url(value)
            return value


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "lessons_count",
            "lessons",
            "owner",
            "is_subscribed",
        ]
        read_only_fields = ["owner"]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from users.models import Subscription

            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False
