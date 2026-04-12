from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ServicePlan, CustomerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role details', {'fields': ('role', 'region', 'account_reference')}),
    )
    list_display = ('username', 'email', 'role', 'region', 'account_reference', 'is_staff')


admin.site.register(ServicePlan)
admin.site.register(CustomerProfile)