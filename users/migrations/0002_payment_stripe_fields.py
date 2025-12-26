# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('cash', 'Наличные'),
                    ('transfer', 'Перевод на счет'),
                    ('stripe', 'Stripe')
                ],
                max_length=20,
                verbose_name='Способ оплаты'
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Ожидает оплаты'),
                    ('paid', 'Оплачено'),
                    ('failed', 'Ошибка оплаты')
                ],
                default='pending',
                max_length=20,
                verbose_name='Статус оплаты'
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_url',
            field=models.URLField(
                blank=True,
                null=True,
                verbose_name='Ссылка на оплату'
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_price_id',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='ID цены в Stripe'
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_product_id',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='ID продукта в Stripe'
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_session_id',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='ID сессии в Stripe'
            ),
        ),
    ]

