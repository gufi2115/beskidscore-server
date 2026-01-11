from django.db import models
from django.contrib.auth import models as auth_models

class Roles(models.TextChoices):

    ADMIN = 'admin', 'admin'
    EDITOR = 'editor', 'editor'
    USER = 'user', 'user'

class UserManager(auth_models.BaseUserManager):

    def create_user(self, first_name, last_name, email, username, password, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        if not first_name:
            raise ValueError("First name must be provided")
        if not last_name:
            raise ValueError("Last name must be provided")
        if not username:
            raise ValueError("Username must be provided")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
        )

        extra_fields.setdefault('roles', Roles.USER)

        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, first_name, last_name, username, password, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
        )

        extra_fields.setdefault('role', Roles.ADMIN)
        user.is_root_admin = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserM(auth_models.AbstractBaseUser):
    objects = UserManager()
    first_name = models.CharField(verbose_name="first name", max_length=255)
    last_name = models.CharField(verbose_name="last name", max_length=255)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    password = models.CharField(verbose_name="password", max_length=255)
    role = models.CharField(choices=Roles.choices, default=Roles.USER,verbose_name="user role", max_length=255)
    username = models.CharField(verbose_name="username", max_length=255, unique=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_root_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name','email']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin