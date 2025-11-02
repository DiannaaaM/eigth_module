from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка, является ли пользователь модератором"""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()


class IsOwner(permissions.BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CourseLessonPermission(permissions.BasePermission):
    """Права доступа для курсов и уроков"""
    def has_permission(self, request, view):
        # Разрешаем доступ только авторизованным
        if not request.user.is_authenticated:
            return False
        
        # Если это POST (создание), проверяем, не является ли пользователь модератором
        if request.method == 'POST':
            is_moderator = request.user.groups.filter(name='Модераторы').exists()
            return not is_moderator  # Модераторы не могут создавать
        
        return True

    def has_object_permission(self, request, view, obj):
        # Получаем владельца объекта
        owner = getattr(obj, 'owner', None)
        
        # Проверяем, является ли пользователь модератором
        is_moderator = request.user.groups.filter(name='Модераторы').exists()
        
        # Если пользователь - модератор
        if is_moderator:
            # Модераторы не могут удалять и создавать новые объекты
            if request.method in ['DELETE', 'POST']:
                return False
            # Но могут просматривать и редактировать любые объекты
            return True
        
        # Если пользователь не модератор - проверяем, является ли он владельцем
        # Если у объекта нет владельца, разрешаем доступ только для чтения
        if owner is None:
            return request.method in ['GET', 'HEAD', 'OPTIONS']
        
        # Проверяем владельца для всех операций
        return owner == request.user

