# Generated by Django 5.0.7 on 2024-07-31 17:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0003_product_archived'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_adress', models.TextField(blank=True, null=True)),
                ('promocode', models.CharField(blank=True, max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('products', models.ManyToManyField(related_name='orders', to='shopapp.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
