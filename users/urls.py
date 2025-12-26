from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import PaymentViewSet, UserViewSet, UserRegistrationView, PaymentStatusAPIView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # JWT авторизация (доступна без токена)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Регистрация (доступна без токена)
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    # Проверка статуса платежа
    path('payments/<int:payment_id>/status/', PaymentStatusAPIView.as_view(), name='payment-status'),
]

