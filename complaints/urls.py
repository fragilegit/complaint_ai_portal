from django.urls import path
from . import views

urlpatterns = [
    path('customer/', views.customer_complaint_list, name='customer-complaint-list'),
    path('customer/new/', views.customer_complaint_create, name='customer-complaint-create'),
    path('agent/', views.agent_work_queue, name='agent-work-queue'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('<int:pk>/', views.complaint_detail, name='complaint-detail'),
    path('<int:pk>/update/', views.complaint_update, name='complaint-update'),
]
