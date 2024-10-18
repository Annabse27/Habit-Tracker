from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """Менеджер для создания пользователей и суперпользователей с Email в качестве ключа аутентификации."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Поле Email обязательно.'))

        # Простая проверка на корректность email
        if '@' not in email:
            raise ValueError(_('Некорректный email адрес.'))

        email = self.normalize_email(email)

        # Проверка на дубликат email
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_('Пользователь с таким email уже существует.'))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        try:
            user.save(using=self._db)
        except IntegrityError:
            raise ValidationError(_('Не удалось создать пользователя. Пользователь с таким email уже существует.'))

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с аутентификацией по Email."""

    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Введите ваш действующий email. Используется для аутентификации.')
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Телефон',
        help_text=_('Необязательно. Можно указать для связи.')
    )
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Telegram Username',
        help_text=_('Введите ваш ник в Telegram для связи с ботом.')
    )
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Telegram Chat ID',
        help_text=_('Чат ID используется для отправки уведомлений через Telegram.')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Указывает, активен ли пользователь. Отключите это поле вместо удаления аккаунта.')
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=_('Определяет, имеет ли пользователь доступ к административной части сайта.')
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Дата регистрации пользователя.')
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Аутентификация по email
    REQUIRED_FIELDS = []  # Нет обязательных полей, кроме email и пароля

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

