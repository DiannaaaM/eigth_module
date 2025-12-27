"""
Задачи Celery для приложения users
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import User


@shared_task
def block_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца
    Устанавливает is_active=False для таких пользователей
    Включает пользователей, которые никогда не входили (last_login=None)
    """
    try:
        one_month_ago = timezone.now() - timedelta(days=30)
        
        # Находим пользователей, которые не заходили более месяца
        # или никогда не входили (last_login=None)
        from django.db.models import Q
        
        inactive_users = User.objects.filter(
            Q(last_login__lt=one_month_ago) | Q(last_login__isnull=True)
        ).exclude(
            is_active=False  # Исключаем уже заблокированных
        )
        
        count = inactive_users.count()
        
        if count > 0:
            inactive_users.update(is_active=False)
            return f"Заблокировано {count} неактивных пользователей"
        else:
            return "Нет неактивных пользователей для блокировки"
            
    except Exception as e:
        return f"Ошибка при блокировке неактивных пользователей: {str(e)}"

