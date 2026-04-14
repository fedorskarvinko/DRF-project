from django.urls import include, path
from rest_framework.routers import DefaultRouter

from materials.views import (
    CourseViewSet,
    LessonListCreateView,
    LessonRetrieveUpdateDestroyView,
)

# Роутер для ViewSet (курсы)
router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    # Маршруты от роутера
    path("", include(router.urls)),
    # Маршруты для уроков (Generic-классы)
    path("lessons/", LessonListCreateView.as_view(), name="lesson-list"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyView.as_view(),
        name="lesson-detail",
    ),
]
