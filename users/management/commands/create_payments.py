from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from users.models import User, Payment
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает тестовые данные для платежей'

    def handle(self, *args, **options):
        # Получаем или создаем пользователей
        users = []
        for i in range(3):
            user, created = User.objects.get_or_create(
                email=f'user{i+1}@example.com',
                defaults={
                    'first_name': f'User{i+1}',
                    'last_name': 'Test',
                    'phone': f'+7900123456{i}',
                    'city': 'Москва' if i == 0 else 'Санкт-Петербург' if i == 1 else 'Казань',
                }
            )
            if created:
                user.set_password('test123456')
                user.save()
            users.append(user)
            self.stdout.write(self.style.SUCCESS(f'Пользователь {"создан" if created else "найден"}: {user.email}'))

        # Получаем или создаем курсы
        courses = []
        for i in range(2):
            course, created = Course.objects.get_or_create(
                title=f'Курс {i+1}',
                defaults={
                    'description': f'Описание курса {i+1}',
                }
            )
            courses.append(course)
            self.stdout.write(self.style.SUCCESS(f'Курс {"создан" if created else "найден"}: {course.title}'))

        # Получаем или создаем уроки
        lessons = []
        for course in courses:
            for i in range(3):
                lesson, created = Lesson.objects.get_or_create(
                    course=course,
                    title=f'Урок {i+1} курса "{course.title}"',
                    defaults={
                        'description': f'Описание урока {i+1}',
                        'video_link': f'https://example.com/video/{course.id}/{i+1}',
                    }
                )
                lessons.append(lesson)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Урок создан: {lesson.title}'))

        # Создаем платежи
        payments_data = [
            # Платежи за курсы
            {'user': users[0], 'course': courses[0], 'lesson': None, 'amount': Decimal('5000.00'), 'payment_method': 'transfer'},
            {'user': users[1], 'course': courses[0], 'lesson': None, 'amount': Decimal('5000.00'), 'payment_method': 'cash'},
            {'user': users[2], 'course': courses[1], 'lesson': None, 'amount': Decimal('7500.00'), 'payment_method': 'transfer'},
            
            # Платежи за уроки
            {'user': users[0], 'course': None, 'lesson': lessons[0], 'amount': Decimal('500.00'), 'payment_method': 'cash'},
            {'user': users[1], 'course': None, 'lesson': lessons[1], 'amount': Decimal('500.00'), 'payment_method': 'transfer'},
            {'user': users[2], 'course': None, 'lesson': lessons[2], 'amount': Decimal('750.00'), 'payment_method': 'transfer'},
        ]

        created_count = 0
        from django.utils import timezone
        from datetime import timedelta
        
        for i, payment_data in enumerate(payments_data):
            # Создаем платеж с разными датами (сейчас, вчера, позавчера и т.д.)
            if 'payment_date' not in payment_data:
                payment_data['payment_date'] = timezone.now() - timedelta(days=i)
            
            payment = Payment(**payment_data)
            payment.save()
            created_count += 1
            payment_info = f"{payment.user.email} - {payment.course.title if payment.course else payment.lesson.title} - {payment.amount} руб."
            self.stdout.write(self.style.SUCCESS(f'Платеж создан: {payment_info}'))

        self.stdout.write(self.style.SUCCESS(f'\nВсего создано платежей: {created_count}'))

