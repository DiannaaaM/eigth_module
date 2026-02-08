from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.shortcuts import get_object_or_404
from .models import Payment, User
from .serializers import (
    PaymentSerializer,
    PaymentCreateSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    UserDetailSerializer
)
from .services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session,
    retrieve_stripe_session,
)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для платежей с фильтрацией"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method', 'payment_status']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def get_queryset(self):
        """Пользователи видят только свои платежи, кроме суперпользователей"""
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    @extend_schema(
        summary='Создать платеж',
        description='Создает новый платеж. Для оплаты через Stripe автоматически создается сессия оплаты.',
        request=PaymentCreateSerializer,
        responses={201: PaymentSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Определяем курс или урок для получения названия
        course = serializer.validated_data.get('course')
        lesson = serializer.validated_data.get('lesson')
        amount = serializer.validated_data.get('amount')
        payment_method = serializer.validated_data.get('payment_method', 'transfer')
        
        # Создаем платеж
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            lesson=lesson,
            amount=amount,
            payment_method=payment_method,
        )
        
        # Если метод оплаты - Stripe, создаем сессию
        if payment_method == 'stripe':
            try:
                # Определяем название продукта
                if course:
                    product_name = course.title
                    product_description = course.description or f'Курс: {course.title}'
                elif lesson:
                    product_name = lesson.title
                    product_description = lesson.description or f'Урок: {lesson.title}'
                else:
                    product_name = 'Платеж'
                    product_description = 'Платеж за обучение'
                
                # Создаем продукт в Stripe
                product_data = create_stripe_product(product_name, product_description)
                payment.stripe_product_id = product_data['id']
                
                # Создаем цену в Stripe
                price_data = create_stripe_price(product_data['id'], amount)
                payment.stripe_price_id = price_data['id']
                
                # Создаем сессию оплаты
                success_url = f"{request.scheme}://{request.get_host()}/api/payments/{payment.id}/success/"
                cancel_url = f"{request.scheme}://{request.get_host()}/api/payments/{payment.id}/cancel/"
                session_data = create_stripe_checkout_session(
                    price_data['id'],
                    success_url,
                    cancel_url
                )
                payment.stripe_session_id = session_data['id']
                payment.payment_url = session_data['url']
                payment.save()
                
            except Exception as e:
                payment.payment_status = 'failed'
                payment.save()
                return Response(
                    {'error': f'Ошибка при создании сессии оплаты: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        response_serializer = PaymentSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


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

    @extend_schema(
        summary='Получить информацию о текущем пользователе',
        description='Возвращает детальную информацию о текущем аутентифицированном пользователе',
        responses={200: UserDetailSerializer}
    )
    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):
        """Получить информацию о текущем пользователе"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary='Обновить информацию о текущем пользователе',
        description='Обновляет информацию о текущем аутентифицированном пользователе',
        request=UserSerializer,
        responses={200: UserSerializer}
    )
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


class PaymentStatusAPIView(APIView):
    """Проверка статуса платежа через Stripe"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Проверить статус платежа',
        description='Проверяет статус платежа в Stripe по ID сессии',
        parameters=[
            OpenApiParameter(
                name='payment_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID платежа'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=PaymentSerializer,
                description='Данные платежа со статусом'
            ),
            404: OpenApiResponse(description='Платеж не найден'),
        }
    )
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        # Если платеж через Stripe, проверяем статус
        if payment.payment_method == 'stripe' and payment.stripe_session_id:
            try:
                session_data = retrieve_stripe_session(payment.stripe_session_id)
                
                # Обновляем статус платежа
                if session_data['payment_status'] == 'paid':
                    payment.payment_status = 'paid'
                elif session_data['payment_status'] == 'unpaid':
                    payment.payment_status = 'pending'
                else:
                    payment.payment_status = 'failed'
                
                payment.save()
            except Exception as e:
                return Response(
                    {'error': f'Ошибка при проверке статуса: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

