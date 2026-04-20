from django.db import models

from config import settings


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    preview = models.ImageField(
        upload_to="courses/previews/", verbose_name="Превью", blank=True, null=True
    )
    description = models.TextField(verbose_name="Описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    last_notification_time = models.DateTimeField(null=True, blank=True, verbose_name='Время последнего уведомления')

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    preview = models.ImageField(
        upload_to="lessons/previews/", verbose_name="Превью", blank=True, null=True
    )
    video_link = models.URLField(verbose_name="Ссылка на видео", blank=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["id"]

    def __str__(self):
        return self.title
