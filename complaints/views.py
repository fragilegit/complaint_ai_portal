from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Complaint

# Create your views here.

@login_required
def customer_complaint_list(request):
    complaints = Complaint.objects.filter(customer=request.user).select_related('assigned_agent')
    return render(request, 'complaints/customer_list.html', {'complaints': complaints})


@login_required
def agent_work_queue(request):
    if not request.user.is_agent and not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    complaints = Complaint.objects.filter(assigned_agent=request.user).select_related('customer').order_by('created_at')
    return render(request, 'complaints/agent_queue.html', {'complaints': complaints})

@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    by_status = Complaint.objects.values('status').annotate(total=Count('id')).order_by('status')
    by_category = Complaint.objects.values('category').annotate(total=Count('id')).order_by('category')
    avg_resolution = Complaint.objects.filter(resolved_at__isnull=False).annotate(
        resolution_time=ExpressionWrapper(F('resolved_at') - F('created_at'), output_field=DurationField())
    ).aggregate(avg=Avg('resolution_time'))['avg']

    sla_cutoff = timezone.now() - timedelta(days=settings.SLA_BREACH_DAYS)
    breached = Complaint.objects.filter(
        Q(status__in=[Complaint.Status.OPEN, Complaint.Status.IN_PROGRESS, Complaint.Status.ESCALATED]),
        created_at__lt=sla_cutoff,
    ).select_related('customer', 'assigned_agent')

    recent = Complaint.objects.select_related('customer', 'assigned_agent')[:10]
    context = {
        'by_status': by_status,
        'by_category': by_category,
        'avg_resolution': avg_resolution,
        'breached': breached,
        'recent': recent,
        'sla_days': settings.SLA_BREACH_DAYS,
    }
    return render(request, 'complaints/admin_dashboard.html', context)
