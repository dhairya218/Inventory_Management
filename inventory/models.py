from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import now



class UserManager(BaseUserManager):
    """
    Custom user manager that allows you to create new users
    """

    def create_user(self, username, password, **extra_fields):
        """
        Creates and saves a new user with the given username and password
        """
        if not username:
            raise ValueError(_('The Username is required'))
        if not extra_fields.get('email'):
            raise ValueError(_('The Email is required'))
        user = self.model(username=username,  **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Creates and saves a new superuser with the given username and password
        """
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.SuperAdmin)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    SuperAdmin = 'SuperAdmin'
    Admin = 'Admin'
    Manager = 'Manager'
    Staff = 'Staff'

    ROLE_CHOICES = (
        (SuperAdmin, 'SuperAdmin'),
        (Admin, 'Admin'),
        (Manager, 'Manager'),
        (Staff, 'Staff')
    )

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    objects = UserManager()

    def __str__(self):
        return self.username


class Unit(models.Model):
    unit_name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.unit_name


class ProductList(models.Model):
    product_id = models.PositiveIntegerField(unique=True, blank=True, null=True)
    product_name = models.CharField(max_length=100, unique=True)
    product_type = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now=True)
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)  # This field should be present


    def __str__(self):
        return self.product_name
    
    def save(self, *args, **kwargs):

        if not self.unit:
            # You can define a default unit here (e.g., the first unit or any specific unit)
            default_unit, created = Unit.objects.get_or_create(unit_name='Default Unit')
            self.unit = default_unit

        if not self.product_id:
            last_product = ProductList.objects.all().order_by('product_id').last()
            if last_product:
                self.product_id = last_product.product_id + 1
            else:
                self.product_id = 1
        super(ProductList, self).save(*args, **kwargs)


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class ProductStock(models.Model):
    product = models.OneToOneField(ProductList, on_delete=models.CASCADE)
    stock_quantity = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.product.product_name} - Stock: {self.stock_quantity}'


class ProductHistory(models.Model):
    product = models.ForeignKey(ProductList, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.product.product_name} - {self.transaction_type} - {self.quantity}'
    


