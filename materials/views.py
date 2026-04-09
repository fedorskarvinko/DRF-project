from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsModerator, IsOwner
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create']:
            # Создавать курсы могут только авторизованные пользователи, не модераторы
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Редактировать могут модераторы или владельцы
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ['destroy']:
            # Удалять могут только владельцы (не модераторы)
            permission_classes = [IsAuthenticated, ~IsModerator & IsOwner]
        else:
            # Просматривать могут все авторизованные пользователи
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Автоматически привязываем создателя к курсу
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            # Модераторы видят все курсы
            return Course.objects.all()
        # Обычные пользователи видят только свои курсы
        return Course.objects.filter(owner=user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            # Создавать уроки могут только авторизованные пользователи, не модераторы
            permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            # Просматривать список могут все авторизованные
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Автоматически привязываем создателя к уроку
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            # Модераторы видят все уроки
            return Lesson.objects.all()
        # Обычные пользователи видят только свои уроки
        return Lesson.objects.filter(owner=user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            # Редактировать могут модераторы или владельцы
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.request.method == 'DELETE':
            # Удалять могут только владельцы (не модераторы)
            permission_classes = [IsAuthenticated, ~IsModerator & IsOwner]
        else:
            # Просматривать могут все авторизованные
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if IsModerator().has_permission(self.request, self):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)
