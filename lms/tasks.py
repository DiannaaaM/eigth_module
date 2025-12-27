"""
Задачи Celery для приложения lms
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, CourseSubscription


@shared_task
def send_course_update_notification(course_id):
    """
    Отправляет уведомления подписанным пользователям об обновлении курса
    
    Args:
        course_id: ID курса, который был обновлен
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = CourseSubscription.objects.filter(course=course)
        
        subscribers = [subscription.user for subscription in subscriptions]
        
        if not subscribers:
            return f"Нет подписчиков на курс '{course.title}'"
        
        subject = f'Обновление курса: {course.title}'
        message = f'Курс "{course.title}" был обновлен. Проверьте новые материалы!'
        
        recipient_list = [user.email for user in subscribers if user.email]
        
        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return f"Уведомления отправлены {len(recipient_list)} подписчикам курса '{course.title}'"
        else:
            return f"Нет email адресов для отправки уведомлений о курсе '{course.title}'"
            
    except Course.DoesNotExist:
        return f"Курс с ID {course_id} не найден"
    except Exception as e:
        return f"Ошибка при отправке уведомлений: {str(e)}"


@shared_task
def check_and_send_lesson_update_notification(lesson_id):
    """
    Проверяет, прошло ли более 4 часов с последнего обновления курса,
    и отправляет уведомления подписанным пользователям об обновлении урока
    
    Args:
        lesson_id: ID урока, который был обновлен
    """
    try:
        from .models import Lesson
        
        lesson = Lesson.objects.select_related('course').get(id=lesson_id)
        course = lesson.course
        
        # Проверяем, когда курс был последний раз обновлен
        now = timezone.now()
        four_hours_ago = now - timedelta(hours=4)
        
        # Проверяем время последнего обновления курса
        if course.updated_at and course.updated_at > four_hours_ago:
            # Курс обновлялся менее 4 часов назад, не отправляем уведомление
            return f"Курс '{course.title}' обновлялся менее 4 часов назад. Уведомление не отправлено."
        
        # Проверяем, есть ли другие уроки, обновленные в последние 4 часа
        recent_lessons = Lesson.objects.filter(
            course=course
        ).exclude(id=lesson_id).filter(
            updated_at__gte=four_hours_ago
        ).exists()
        
        if recent_lessons:
            # Есть другие уроки, обновленные недавно, не отправляем уведомление
            return f"В курсе '{course.title}' есть другие уроки, обновленные менее 4 часов назад. Уведомление не отправлено."
        
        # Отправляем уведомление только если прошло более 4 часов с последнего обновления курса
        subscriptions = CourseSubscription.objects.filter(course=course)
        subscribers = [subscription.user for subscription in subscriptions]
        
        if not subscribers:
            return f"Нет подписчиков на курс '{course.title}'"
        
        subject = f'Обновление курса: {course.title}'
        message = f'В курсе "{course.title}" добавлен новый урок: "{lesson.title}". Проверьте новые материалы!'
        
        recipient_list = [user.email for user in subscribers if user.email]
        
        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return f"Уведомления отправлены {len(recipient_list)} подписчикам курса '{course.title}' об уроке '{lesson.title}'"
        else:
            return f"Нет email адресов для отправки уведомлений о курсе '{course.title}'"
            
    except Exception as e:
        return f"Ошибка при отправке уведомлений об уроке: {str(e)}"

