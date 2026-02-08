from rest_framework import serializers
from lms.models import Course, Lesson
from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежа"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('stripe_product_id', 'stripe_price_id', 'stripe_session_id', 'payment_url', 'payment_status')


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания платежа"""
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        required=False,
        allow_null=True,
    )
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Payment
        fields = ('course', 'lesson', 'amount', 'payment_method')

    def validate(self, attrs):
        if not attrs.get('course') and not attrs.get('lesson'):
            raise serializers.ValidationError('Необходимо указать либо курс, либо урок')
        if attrs.get('course') and attrs.get('lesson'):
            raise serializers.ValidationError('Нельзя указывать одновременно курс и урок')
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя (CRUD)"""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'city')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального представления пользователя"""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'is_active', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')
