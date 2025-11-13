from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
    """ViewSet для курсов"""
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


class LessonListCreateView(ListCreateAPIView):
    """Представление для получения списка уроков и создания нового урока"""
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
        """Устанавливаем владельца при создании урока"""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления урока"""
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


class CourseSubscriptionToggleAPIView(APIView):
    """Управление подпиской пользователя на курс"""
    permission_classes = [IsAuthenticated]

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

