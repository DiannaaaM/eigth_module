from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, User
from .serializers import (
    PaymentSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    UserDetailSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежей с фильтрацией"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей (CRUD)"""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer

    def get_queryset(self):
        """Пользователи видят только свои данные, кроме суперпользователей"""
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):
        """Получить информацию о текущем пользователе"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], url_path='me')
    def update_current_user(self, request):
        """Обновить информацию о текущем пользователе"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(CreateAPIView):
    """Представление для регистрации пользователя (доступно без авторизации)"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []  # Разрешаем регистрацию без авторизации

