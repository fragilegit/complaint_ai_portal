from django.conf import settings
from django.db import models
from django.utils import timezone


class Complaint(models.Model):
    class Category(models.TextChoices):
        BILLING = 'billing', 'Billing'
        NETWORK = 'network', 'Network'
        DEVICE = 'device', 'Device'
        ROAMING = 'roaming', 'Roaming'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        ESCALATED = 'escalated', 'Escalated'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    reference = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    assigned_agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints')
    escalation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.reference

    @property
    def resolution_time_hours(self):
        if self.resolved_at:
            return round((self.resolved_at - self.created_at).total_seconds() / 3600, 2)
        return None

    def can_transition(self, user, current_status, new_status):
        ordered = [self.Status.OPEN, self.Status.IN_PROGRESS, self.Status.ESCALATED, self.Status.RESOLVED, self.Status.CLOSED]
        if getattr(user, 'is_admin_user', False):
            return True
        if not getattr(user, 'is_agent', False):
            return False
        try:
            # return ordered.index(new_status) >= ordered.index(self.status)
            current_index = ordered.index(current_status)
            new_index = ordered.index(new_status)
            
            return new_index == current_index + 1
        except ValueError:
            return False


class ComplaintNote(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.TextField()
    is_resolution_note = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class NetworkFault(models.Model):
    title = models.CharField(max_length=150)
    region = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
