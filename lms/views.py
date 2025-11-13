from rest_framework import viewsets
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from .models import Course, Lesson
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    LessonListSerializer,
    LessonDetailSerializer
)
from .permissions import CourseLessonPermission


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [CourseLessonPermission]

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

