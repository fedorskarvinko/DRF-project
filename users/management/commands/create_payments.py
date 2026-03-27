from django.core.management.base import BaseCommand
from users.models import User, Payment
from materials.models import Course, Lesson
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Создание тестовых платежей'

    def handle(self, *args, **options):
        # Получаем или создаем пользователей
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.WARNING('Нет пользователей. Сначала создайте пользователей.'))
            return

        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        if not courses.exists() and not lessons.exists():
            self.stdout.write(self.style.WARNING('Нет курсов и уроков. Сначала создайте курсы и уроки.'))
            return

        # Очищаем существующие платежи
        Payment.objects.all().delete()

        payment_methods = [method[0] for method in Payment.PaymentMethod.choices]

        for user in users:
            # Создаем несколько платежей для каждого пользователя
            for i in range(3):
                payment_date = datetime.now() - timedelta(days=random.randint(1, 90))

                # Случайно выбираем курс или урок для оплаты
                if random.choice([True, False]) and courses.exists():
                    paid_course = random.choice(courses)
                    paid_lesson = None
                    amount = random.randint(3000, 10000)
                elif lessons.exists():
                    paid_course = None
                    paid_lesson = random.choice(lessons)
                    amount = random.randint(500, 3000)
                else:
                    continue

                payment = Payment.objects.create(
                    user=user,
                    payment_date=payment_date,
                    paid_course=paid_course,
                    paid_lesson=paid_lesson,
                    amount=amount,
                    payment_method=random.choice(payment_methods)
                )

                self.stdout.write(self.style.SUCCESS(f'Создан платеж: {payment}'))

        self.stdout.write(self.style.SUCCESS('Тестовые платежи успешно созданы!'))