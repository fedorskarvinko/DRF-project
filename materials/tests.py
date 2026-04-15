from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import Group
from .models import Course, Lesson
from users.models import Subscription

# Create your tests here.


User = get_user_model()


class LessonTestCase(APITestCase):
    """
    Тестирование CRUD для уроков
    """

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаем пользователей
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            first_name="Обычный",
            last_name="Пользователь",
        )

        self.moderator = User.objects.create_user(
            email="moderator@test.com",
            password="testpass123",
            first_name="Модератор",
            last_name="Пользователь",
        )

        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
            first_name="Другой",
            last_name="Пользователь",
        )

        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator.groups.add(self.moderator_group)

        # Создаем курс
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание тестового курса",
            owner=self.user,
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание тестового урока",
            video_link="https://www.youtube.com/watch?v=test",
            course=self.course,
            owner=self.user,
        )

        # Настраиваем клиент
        self.client = APIClient()

        self.lessons_list_url = "/api/materials/lessons/"
        self.lesson_detail_url = f"/api/materials/lessons/{self.lesson.id}/"
        self.subscriptions_url = "/api/users/subscriptions/"
        self.course_detail_url = f"/api/materials/courses/{self.course.id}/"

    def test_lesson_list_authenticated(self):
        """Тест получения списка уроков для авторизованного пользователя"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("results" in response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_lesson_list_unauthenticated(self):
        """Тест получения списка уроков для неавторизованного пользователя"""
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_owner(self):
        """Тест создания урока владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "video_link": "https://www.youtube.com/watch?v=new",
            "course": self.course.id,
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().owner, self.user)

    def test_lesson_create_moderator(self):
        """Тест создания урока модератором (должно быть запрещено)"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "video_link": "https://www.youtube.com/watch?v=new",
            "course": self.course.id,
        }
        response = self.client.post(self.lessons_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Обновленный заголовок"}
        response = self.client.patch(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновленный заголовок")

    def test_lesson_update_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "Обновлено модератором"}
        response = self.client.patch(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновлено модератором")

    def test_lesson_update_other_user(self):
        """Тест обновления урока другим пользователем (должно быть запрещено)"""
        self.client.force_authenticate(user=self.other_user)
        data = {"title": "Попытка взлома"}
        response = self.client.patch(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user)

        # Проверим, что пользователь видит урок
        response = self.client.get(self.lesson_detail_url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response data: {response.data}")

        # Попробуем удалить
        response = self.client.delete(self.lesson_detail_url)
        print(f"DELETE response status: {response.status_code}")
        print(
            f"DELETE response data: {response.data if hasattr(response, 'data') else 'No data'}"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_moderator(self):
        """Тест удаления урока модератором (должно быть запрещено)"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_other_user(self):
        """Тест удаления урока другим пользователем (должно быть запрещено)"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_video_link_validation(self):
        """Тест валидации ссылки на видео (только youtube)"""
        self.client.force_authenticate(user=self.user)

        # Валидная youtube ссылка
        data_valid = {
            "title": "Урок с youtube",
            "description": "Описание",
            "video_link": "https://www.youtube.com/watch?v=valid",
            "course": self.course.id,
        }
        response = self.client.post(self.lessons_list_url, data_valid)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Невалидная ссылка
        data_invalid = {
            "title": "Урок с плохой ссылкой",
            "description": "Описание",
            "video_link": "https://vimeo.com/123456",
            "course": self.course.id,
        }
        response = self.client.post(self.lessons_list_url, data_invalid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SubscriptionTestCase(APITestCase):
    """
    Тестирование функционала подписок
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="testpass123"
        )

        self.other_user = User.objects.create_user(
            email="other@test.com", password="testpass123"
        )

        self.course = Course.objects.create(
            title="Тестовый курс", description="Описание", owner=self.user
        )

        self.client = APIClient()

        # Правильные URL из show_urls
        self.subscriptions_list_url = "/api/subscriptions/"
        self.subscriptions_toggle_url = "/api/subscriptions/toggle/"
        self.course_detail_url = f"/api/materials/courses/{self.course.id}/"
        self.user_list_url = "/api/users/"
        self.user_detail_url = f"/api/users/{self.user.id}/"
        self.payments_url = "/api/payments/"

    def test_subscription_create(self):
        """Тест создания подписки через toggle"""
        self.client.force_authenticate(user=self.user)
        data = {"course_id": self.course.id}
        response = self.client.post(self.subscriptions_toggle_url, data, format="json")

        print(f"Create response status: {response.status_code}")
        print(f"Create response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(response.data["is_subscribed"])
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_delete(self):
        """Тест удаления подписки через toggle"""
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        data = {"course_id": self.course.id}
        response = self.client.post(self.subscriptions_toggle_url, data, format="json")

        print(f"Delete response status: {response.status_code}")
        print(f"Delete response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(response.data["is_subscribed"])
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_without_auth(self):
        """Тест подписки без авторизации"""
        data = {"course_id": self.course.id}
        response = self.client.post(self.subscriptions_toggle_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_list(self):
        """Тест получения списка подписок"""
        # Создаем подписки
        sub = Subscription.objects.create(user=self.user, course=self.course)
        print(f"Created subscription: {sub.id} for course {self.course.id}")

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.subscriptions_list_url)

        print(f"List response status: {response.status_code}")
        print(f"List response data: {response.data}")
        print(f"Response headers: {response.headers}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру ответа (у ViewSet может быть пагинация)
        if isinstance(response.data, dict) and "results" in response.data:
            # Если используется пагинация
            self.assertGreaterEqual(len(response.data["results"]), 1)
            self.assertEqual(response.data["results"][0]["course"], self.course.id)
        else:
            # Если без пагинации
            self.assertGreaterEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["course"], self.course.id)

    def test_course_is_subscribed_field(self):
        """Тест поля is_subscribed в сериализаторе курса"""
        self.client.force_authenticate(user=self.user)

        # Проверим, что курс доступен
        response = self.client.get(self.course_detail_url)
        print(f"Course detail before subscription: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_subscribed"])

        # Создаем подписку через toggle
        sub_response = self.client.post(
            self.subscriptions_toggle_url, {"course_id": self.course.id}, format="json"
        )
        print(f"Subscription creation: {sub_response.status_code}")
        self.assertEqual(sub_response.status_code, status.HTTP_201_CREATED)

        # Проверяем поле is_subscribed
        response = self.client.get(self.course_detail_url)
        print(f"Course detail after subscription: {response.status_code}")
        print(f"Course data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])

        # Для другого пользователя
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.course_detail_url)
        print(f"Other user course detail: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_subscribed"])

    def test_subscription_invalid_course(self):
        """Тест подписки на несуществующий курс"""
        self.client.force_authenticate(user=self.user)
        data = {"course_id": 9999}
        response = self.client.post(self.subscriptions_toggle_url, data, format="json")

        print(f"Invalid course response: {response.status_code}")
        print(f"Invalid course data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
