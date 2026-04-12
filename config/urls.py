from django.urls import path
from accounts.views import role_dashboard_redirect, login_view

urlpatterns = [
    path('', role_dashboard_redirect, name='dashboard'),
    path('login/', login_view, name='login'),
]