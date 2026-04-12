from django.urls import path
from accounts.views import role_dashboard_redirect, login_view, logout_view

urlpatterns = [
    path('', role_dashboard_redirect, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]