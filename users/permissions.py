from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """
    Проверка, является ли пользователь модератором
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """
    Проверка, является ли пользователь владельцем объекта
    """

    def has_object_permission(self, request, view, obj):
        # Проверяем, есть ли у объекта поле owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешение на редактирование только для владельца
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Для остальных методов проверяем владельца
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False