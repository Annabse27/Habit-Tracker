# Generated by Django 5.1.2 on 2024-10-16 11:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Habit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(help_text='Описание действия', max_length=255)),
                ('time', models.TimeField(help_text='Время выполнения привычки')),
                ('place', models.CharField(help_text='Место выполнения привычки', max_length=255)),
                ('is_pleasant', models.BooleanField(default=False, help_text='Это приятная привычка?')),
                ('frequency', models.PositiveIntegerField(default=1, help_text='Периодичность выполнения в днях')),
                ('reward', models.CharField(blank=True, help_text='Вознаграждение за выполнение', max_length=255, null=True)),
                ('duration', models.PositiveIntegerField(help_text='Время на выполнение в секундах')),
                ('is_public', models.BooleanField(default=False, help_text='Привычка публичная?')),
                ('next_reminder', models.DateTimeField(blank=True, help_text='Дата и время следующего напоминания', null=True)),
                ('linked_habit', models.ForeignKey(blank=True, help_text='Связанная привычка (для полезной привычки)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='linked_to', to='habits.habit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='habits', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Привычка',
                'verbose_name_plural': 'Привычки',
                'ordering': ['next_reminder'],
            },
        ),
    ]
