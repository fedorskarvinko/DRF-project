from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Subscription
from materials.models import Course
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_course_update_email(course_id, user_email, user_name, course_title):
    """
    Отправка письма пользователю об обновлении курса
    """
    try:
        subject = f"Обновление курса: {course_title}"
        message = f"""
        Здравствуйте, {user_name}!

        Курс "{course_title}" был обновлен. 
        Новые материалы уже доступны для изучения.

        Ссылка на курс: http://localhost:8000/api/materials/courses/{course_id}/

        С уважением,
        Команда LMS System
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        logger.info(f"Email sent to {user_email} about course {course_title}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")
        return False


@shared_task
def notify_course_subscribers(course_id, course_title, last_update_time):
    """
    Уведомление всех подписчиков курса об обновлении
    """
    try:
        # Получаем всех подписчиков курса
        subscriptions = Subscription.objects.filter(course_id=course_id).select_related(
            "user"
        )

        if not subscriptions.exists():
            logger.info(f"No subscribers for course {course_title}")
            return {"status": "no_subscribers", "count": 0}

        sent_count = 0
        for subscription in subscriptions:
            user = subscription.user
            # Отправляем письмо каждому подписчику
            send_course_update_email.delay(
                course_id=course_id,
                user_email=user.email,
                user_name=user.first_name or user.email,
                course_title=course_title,
            )
            sent_count += 1

        logger.info(
            f"Notifications sent to {sent_count} subscribers for course {course_title}"
        )
        return {"status": "success", "count": sent_count}

    except Exception as e:
        logger.error(f"Failed to notify subscribers for course {course_id}: {e}")
        return {"status": "error", "error": str(e)}


@shared_task
def deactivate_inactive_users():
    """
    Блокировка пользователей, которые не заходили более месяца
    """
    try:
        one_month_ago = timezone.now() - timedelta(days=30)

        # Находим активных пользователей, которые не заходили более месяца
        inactive_users = User.objects.filter(
            is_active=True, last_login__lt=one_month_ago
        )

        count = inactive_users.count()

        if count > 0:
            # Блокируем пользователей
            updated_count = inactive_users.update(is_active=False)
            logger.info(f"Deactivated {updated_count} inactive users")

            # Отправляем уведомления заблокированным пользователям
            for user in inactive_users:
                send_account_blocked_email.delay(
                    user.email, user.first_name or user.email
                )

            return {"status": "success", "deactivated_count": updated_count}
        else:
            logger.info("No inactive users found")
            return {"status": "success", "deactivated_count": 0}

    except Exception as e:
        logger.error(f"Failed to deactivate inactive users: {e}")
        return {"status": "error", "error": str(e)}


@shared_task
def send_account_blocked_email(user_email, user_name):
    """
    Отправка письма о блокировке аккаунта
    """
    try:
        subject = "Ваш аккаунт был заблокирован"
        message = f"""
        Здравствуйте, {user_name}!

        Ваш аккаунт был автоматически заблокирован из-за отсутствия активности более месяца.

        Для разблокировки обратитесь в службу поддержки или войдите в систему.

        С уважением,
        Команда LMS System
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        logger.info(f"Block notification sent to {user_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send block notification to {user_email}: {e}")
        return False
