from rest_framework.serializers import ValidationError


class YouTubeUrlValidator:
    """
    Валидатор для проверки, что ссылка ведет на youtube.com
    """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Если значение не является словарем (для работы с сериализатором)
        if isinstance(value, dict):
            video_link = value.get(self.field)
        else:
            video_linc = value

        if (
            video_link
            and "youtube.com" not in video_link
            and "youtu.be" not in video_link
        ):
            raise ValidationError(
                f"Ссылка должна быть на youtube.com. Текущая ссылка: {video_link}"
            )


def validate_youtube_url(value):
    """
    Функция-валидатор для проверки ссылок на youtube
    """
    if value and "youtube.com" not in value and "youtu.be" not in value:
        raise ValidationError(
            f"Ссылка должна быть на youtube.com. Текущая ссылка: {value}"
        )
