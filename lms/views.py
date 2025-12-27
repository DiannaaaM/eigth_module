from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import Course, Lesson, CourseSubscription
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    LessonListSerializer,
    LessonDetailSerializer
)
from .permissions import CourseLessonPermission
from .paginators import CoursePagination, LessonPagination


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления курсами.
    
    - Список курсов: GET /api/courses/
    - Создание курса: POST /api/courses/
    - Детали курса: GET /api/courses/{id}/
    - Обновление курса: PUT/PATCH /api/courses/{id}/
    - Удаление курса: DELETE /api/courses/{id}/
    
    Модераторы видят все курсы, обычные пользователи - только свои.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [CourseLessonPermission]
    pagination_class = CoursePagination

    def get_queryset(self):
        """Фильтрация queryset в зависимости от прав пользователя"""
        user = self.request.user
        is_moderator = user.groups.filter(name='Модераторы').exists()

        if is_moderator:
            # Модераторы видят все курсы
            return Course.objects.all()
        else:
            # Обычные пользователи видят только свои курсы
            return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Устанавливаем владельца при создании курса"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """Обновляет курс и отправляет уведомления подписчикам"""
        instance = serializer.save()
        # Отправляем уведомления асинхронно
        from .tasks import send_course_update_notification
        send_course_update_notification.delay(instance.id)


class LessonListCreateView(ListCreateAPIView):
    """
    Представление для получения списка уроков и создания нового урока.
    
    - Список уроков: GET /api/lessons/
    - Создание урока: POST /api/lessons/
    
    Модераторы видят все уроки, обычные пользователи - только свои.
    Видео-ссылки должны быть только с YouTube.
    """
    queryset = Lesson.objects.all()
    permission_classes = [CourseLessonPermission]
    pagination_class = LessonPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LessonListSerializer
        return LessonSerializer

    def get_queryset(self):
        """Фильтрация queryset в зависимости от прав пользователя"""
        user = self.request.user
        is_moderator = user.groups.filter(name='Модераторы').exists()

        if is_moderator:
            # Модераторы видят все уроки
            return Lesson.objects.all()
        else:
            # Обычные пользователи видят только свои уроки
            return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Устанавливаем владельца при создании урока и отправляет уведомления"""
        lesson = serializer.save(owner=self.request.user)
        # Отправляем уведомления асинхронно с проверкой на 4 часа
        from .tasks import check_and_send_lesson_update_notification
        check_and_send_lesson_update_notification.delay(lesson.id)


class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Представление для получения, обновления и удаления урока.
    
    - Детали урока: GET /api/lessons/{id}/
    - Обновление урока: PUT/PATCH /api/lessons/{id}/
    - Удаление урока: DELETE /api/lessons/{id}/
    
    Модераторы могут управлять всеми уроками, обычные пользователи - только своими.
    """
    queryset = Lesson.objects.all()
    permission_classes = [CourseLessonPermission]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LessonDetailSerializer
        return LessonSerializer

    def get_queryset(self):
        """Фильтрация queryset в зависимости от прав пользователя"""
        user = self.request.user
        is_moderator = user.groups.filter(name='Модераторы').exists()

        if is_moderator:
            # Модераторы видят все уроки
            return Lesson.objects.all()
        else:
            # Обычные пользователи видят только свои уроки
            return Lesson.objects.filter(owner=user)

    def perform_update(self, serializer):
        """Обновляет урок и отправляет уведомления подписчикам с проверкой на 4 часа"""
        lesson = serializer.save()
        # Отправляем уведомления асинхронно с проверкой на 4 часа
        from .tasks import check_and_send_lesson_update_notification
        check_and_send_lesson_update_notification.delay(lesson.id)


class CourseSubscriptionToggleAPIView(APIView):
    """Управление подпиской пользователя на курс"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Переключить подписку на курс',
        description='Добавляет или удаляет подписку пользователя на курс',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'course': {
                        'type': 'integer',
                        'description': 'ID курса'
                    }
                },
                'required': ['course']
            }
        },
        responses={
            200: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                },
                description='Результат операции'
            ),
            400: OpenApiResponse(description='Ошибка валидации'),
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course')

        if not course_id:
            return Response({'message': 'Не передан идентификатор курса'}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, pk=course_id)
        subscription_qs = CourseSubscription.objects.filter(user=user, course=course)

        if subscription_qs.exists():
            subscription_qs.delete()
            message = 'Подписка удалена'
        else:
            CourseSubscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'

        return Response({'message': message}, status=status.HTTP_200_OK)

