from django import forms
from .models import Complaint, ComplaintNote
from accounts.models import User


class CustomerComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}


class ComplaintUpdateForm(forms.ModelForm):
    internal_note = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    is_resolution_note = forms.BooleanField(required=False)

    class Meta:
        model = Complaint
        fields = ['status', 'assigned_agent', 'escalation_reason']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['assigned_agent'].queryset = User.objects.filter(role=User.Role.AGENT)
        if user.is_agent and not user.is_admin_user:
            self.fields['assigned_agent'].disabled = True

    def save_note(self, complaint, author):
        note = self.cleaned_data.get('internal_note')
        if note:
            ComplaintNote.objects.create(
                complaint=complaint,
                author=author,
                note=note,
                is_resolution_note=self.cleaned_data.get('is_resolution_note', False),
            )
