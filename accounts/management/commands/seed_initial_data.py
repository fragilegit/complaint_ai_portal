from datetime import timedelta, date
from decimal import Decimal
import random

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User, ServicePlan, CustomerProfile
from complaints.models import Complaint, ComplaintNote, NetworkFault


class Command(BaseCommand):
    help = 'Seed initial sample data if not already present.'

    def handle(self, *args, **kwargs):
        if User.objects.filter(username='admin1').exists() and Complaint.objects.exists():
            self.stdout.write(self.style.SUCCESS('Seed data already present.'))
            return

        password = make_password('Password123!')
        plans = {
            'Basic': ServicePlan.objects.get_or_create(name='Basic', defaults={
                'monthly_price': Decimal('29.99'), 'data_allowance_gb': 10, 'call_minutes': 300, 'sms_allowance': 100
            })[0],
            'Standard': ServicePlan.objects.get_or_create(name='Standard', defaults={
                'monthly_price': Decimal('49.99'), 'data_allowance_gb': 50, 'call_minutes': 1000, 'sms_allowance': 500
            })[0],
            'Premium': ServicePlan.objects.get_or_create(name='Premium', defaults={
                'monthly_price': Decimal('79.99'), 'data_allowance_gb': 200, 'call_minutes': 5000, 'sms_allowance': 2000
            })[0],
        }

        admin = User.objects.get_or_create(
            username='admin1',
            defaults={'email': 'admin@example.com', 'role': 'admin', 'is_staff': True, 'is_superuser': True, 'password': password},
        )[0]

        agents = []
        for i in range(1, 4):
            agent = User.objects.get_or_create(
                username=f'agent{i}',
                defaults={'email': f'agent{i}@example.com', 'role': 'agent', 'is_staff': True, 'password': password},
            )[0]
            agents.append(agent)

        regions = ['North', 'South', 'East', 'West', 'Central']
        customers = []
        for i in range(1, 6):
            customer = User.objects.get_or_create(
                username=f'customer{i}',
                defaults={
                    'email': f'customer{i}@example.com',
                    'role': 'customer',
                    'password': password,
                    'region': regions[i - 1],
                    'account_reference': f'ACC-100{i}',
                },
            )[0]
            CustomerProfile.objects.get_or_create(
                user=customer,
                defaults={
                    'current_plan': list(plans.values())[(i - 1) % 3],
                    'current_balance': Decimal(str(20 * i + 5.50)),
                    'data_used_gb': Decimal(str(2.5 * i)),
                    'phone_number': f'+155500000{i}',
                    'address': f'{i} Main Street',
                    'last_payment_amount': Decimal('49.99'),
                    'last_payment_date': date.today() - timedelta(days=i * 3),
                },
            )
            customers.append(customer)

        fault_defaults = [
            {'title': 'North region fibre outage', 'region': 'North', 'description': 'Intermittent fibre outage affecting broadband services.', 'is_active': True},
            {'title': 'Central tower maintenance', 'region': 'Central', 'description': 'Scheduled maintenance affecting mobile data speeds.', 'is_active': True},
        ]
        for item in fault_defaults:
            NetworkFault.objects.get_or_create(title=item['title'], defaults=item)

        categories = [choice for choice, _ in Complaint.Category.choices]
        statuses = [choice for choice, _ in Complaint.Status.choices]
        now = timezone.now()
        for i in range(1, 16):
            created_at = now - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))
            complaint, created = Complaint.objects.get_or_create(
                reference=f'CMP-{1000 + i}',
                defaults={
                    'customer': customers[(i - 1) % len(customers)],
                    'category': categories[(i - 1) % len(categories)],
                    'description': f'Sample complaint description #{i}. Customer reports an issue requiring follow-up.',
                    'status': statuses[(i - 1) % len(statuses)],
                    'assigned_agent': agents[(i - 1) % len(agents)],
                    'escalation_reason': 'High priority customer impact' if i % 5 == 0 else '',
                    'created_at': created_at,
                    'updated_at': created_at + timedelta(hours=random.randint(1, 48)),
                },
            )
            if created:
                if complaint.status in [Complaint.Status.RESOLVED, Complaint.Status.CLOSED]:
                    complaint.resolved_at = complaint.updated_at
                    complaint.save(update_fields=['resolved_at'])
                ComplaintNote.objects.create(
                    complaint=complaint,
                    author=agents[(i - 1) % len(agents)],
                    note=f'Initial investigation note for complaint {complaint.reference}.',
                    is_resolution_note=complaint.status in [Complaint.Status.RESOLVED, Complaint.Status.CLOSED],
                )

        self.stdout.write(self.style.SUCCESS('Sample data seeded successfully.'))
