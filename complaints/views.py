from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CustomerComplaintForm, ComplaintUpdateForm
from .models import Complaint

# Create your views here.

@login_required
def customer_complaint_list(request):
    complaints = Complaint.objects.filter(customer=request.user).select_related('assigned_agent')
    return render(request, 'complaints/customer_list.html', {'complaints': complaints})


@login_required
def customer_complaint_create(request):
    if not request.user.is_customer:
        messages.error(request, 'Only customers can submit complaints.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomerComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.customer = request.user
            complaint.reference = f'CMP-{timezone.now().strftime("%Y%m%d%H%M%S")}'
            complaint.save()
            messages.success(request, 'Complaint submitted successfully.')
            return redirect('customer-complaint-list')
    else:
        form = CustomerComplaintForm()

    return render(request, 'complaints/customer_form.html', {'form': form})


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint.objects.select_related('customer', 'assigned_agent').prefetch_related('notes__author'), pk=pk)
    if request.user.is_customer and complaint.customer_id != request.user.id:
        messages.error(request, 'You are not allowed to view this complaint.')
        return redirect('customer-complaint-list')
    return render(request, 'complaints/detail.html', {'complaint': complaint})


@login_required
def complaint_update(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.user.is_customer:
        messages.error(request, 'Customers cannot update complaints.')
        return redirect('complaint-detail', pk=pk)

    if request.user.is_agent and complaint.assigned_agent_id != request.user.id and not request.user.is_admin_user:
        messages.error(request, 'Agents may only update complaints assigned to them.')
        return redirect('agent-work-queue')

    if request.method == 'POST':
        original_complaint = Complaint.objects.get(pk=pk)
        current_status = original_complaint.status
        form = ComplaintUpdateForm(request.POST, instance=complaint, user=request.user)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            if not complaint.can_transition(request.user, current_status, new_status):
                messages.error(request, 'Invalid workflow transition for your role.')
                return redirect('complaint-detail', pk=pk)
            updated = form.save(commit=False)
            if new_status == Complaint.Status.RESOLVED and not updated.resolved_at:
                updated.resolved_at = timezone.now()
            updated.save()
            form.save_note(updated, request.user)
            messages.success(request, 'Complaint updated successfully.')
            return redirect('complaint-detail', pk=pk)
    else:
        form = ComplaintUpdateForm(instance=complaint, user=request.user)

    return render(request, 'complaints/update.html', {'form': form, 'complaint': complaint})


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
