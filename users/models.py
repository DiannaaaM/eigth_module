from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с email в качестве логина"""
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватарка')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель платежа"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(verbose_name='Дата оплаты')
    course = models.ForeignKey(
        'lms.Course',
        on_delete=models.CASCADE,
        related_name='payments',
        blank=True,
        null=True,
        verbose_name='Оплаченный курс'
    )
    lesson = models.ForeignKey(
        'lms.Lesson',
        on_delete=models.CASCADE,
        related_name='payments',
        blank=True,
        null=True,
        verbose_name='Оплаченный урок'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Способ оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        payment_for = self.course.title if self.course else (self.lesson.title if self.lesson else 'Не указано')
        return f"{self.user.email} - {payment_for} - {self.amount} руб."

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.course and not self.lesson:
            raise ValidationError('Необходимо указать либо курс, либо урок')
        if self.course and self.lesson:
            raise ValidationError('Нельзя указывать одновременно курс и урок')

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.payment_date:
            self.payment_date = timezone.now()
        self.full_clean()
        super().save(*args, **kwargs)

