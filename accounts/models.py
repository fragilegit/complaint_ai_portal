from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        AGENT = 'agent', 'Agent'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    region = models.CharField(max_length=100, blank=True)
    account_reference = models.CharField(max_length=50, unique=True, null=True, blank=True)

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_agent(self):
        return self.role == self.Role.AGENT

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class ServicePlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    data_allowance_gb = models.PositiveIntegerField()
    call_minutes = models.PositiveIntegerField()
    sms_allowance = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    current_plan = models.ForeignKey(ServicePlan, on_delete=models.PROTECT)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_used_gb = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    phone_number = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    last_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} profile'
