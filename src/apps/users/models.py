# apps/users/models.py
from apps.common.choices import (GENDER_CHOICES, SOCIAL_LOGIN_CHOICES,
                                 USER_TYPE_CHOICES,
                                 VERIFICATION_STATUS_CHOICES)
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "admin")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    user_image = models.CharField(max_length=255, blank=True, null=True)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="regular"
    )
    social_id = models.CharField(max_length=100, blank=True, null=True)
    social_login = models.CharField(
        max_length=10, choices=SOCIAL_LOGIN_CHOICES, default="none"
    )
    verified_email = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True)

    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number", "birth_date"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "User"  # 테이블 이름을 'User'로 지정


class BusinessUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="business_profile"
    )
    business_number = models.CharField(max_length=20)
    business_document = models.FileField(upload_to="business_documents/")
    business_email = models.EmailField()
    business_phonenumber = models.CharField(max_length=20)
    business_address = models.CharField(max_length=255)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=30, choices=VERIFICATION_STATUS_CHOICES, default="pending"
    )


class WithdrawManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    withdraw_date = models.DateTimeField()
    withdraw_reason = models.TextField(null=True, blank=True)
