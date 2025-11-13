from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает группу модераторов с необходимыми правами'

    def handle(self, *args, **options):
        # Создаем или получаем группу модераторов
        group, created = Group.objects.get_or_create(name='Модераторы')
        
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модераторы" создана'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Модераторы" уже существует'))

        # Получаем ContentType для Course и Lesson
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        # Получаем разрешения для курсов
        course_permissions = Permission.objects.filter(
            content_type=course_content_type
        ).exclude(codename__in=['add_course', 'delete_course'])

        # Получаем разрешения для уроков
        lesson_permissions = Permission.objects.filter(
            content_type=lesson_content_type
        ).exclude(codename__in=['add_lesson', 'delete_lesson'])

        # Добавляем разрешения в группу
        all_permissions = list(course_permissions) + list(lesson_permissions)
        
        for permission in all_permissions:
            group.permissions.add(permission)

        self.stdout.write(
            self.style.SUCCESS(
                f'В группу "Модераторы" добавлено {len(all_permissions)} разрешений:\n'
                f'- Просмотр и изменение курсов (без создания и удаления)\n'
                f'- Просмотр и изменение уроков (без создания и удаления)'
            )
        )

