from django.contrib import admin

# Register your models here.

from .models import Complaint, ComplaintNote, NetworkFault


class ComplaintNoteInline(admin.TabularInline):
    model = ComplaintNote
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('reference', 'customer', 'category', 'status', 'assigned_agent', 'created_at', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('reference', 'customer__username', 'customer__account_reference')
    inlines = [ComplaintNoteInline]


admin.site.register(NetworkFault)

