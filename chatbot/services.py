import os
from groq import Groq

from accounts.models import CustomerProfile
from complaints.models import Complaint, NetworkFault
from .models import ChatMessage
from django.conf import settings

MODEL_NAME = 'llama-3.1-8b-instant'
SYSTEM_PROMPT = (
    'You are a customer support assistant. Answer only using the supplied customer context. '
    f"All money values are in {settings.DEFAULT_CURRENCY}."
    f"Use {settings.CURRENCY_SYMBOL} when presenting balances."
    'Do not guess or invent facts. If the context does not contain the answer, say that clearly. '
    'Keep responses concise and helpful.'
)


def build_customer_context(user):
    profile = CustomerProfile.objects.select_related('current_plan').get(user=user)
    open_complaints = Complaint.objects.filter(customer=user).exclude(status=Complaint.Status.CLOSED)
    active_faults = NetworkFault.objects.filter(region=user.region, is_active=True)
    complaint_summary = [
        {
            'reference': c.reference,
            'category': c.category,
            'status': c.status,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for c in open_complaints[:5]
    ]
    faults = [
        {'title': f.title, 'description': f.description, 'region': f.region}
        for f in active_faults
    ]
    return {
        'account_reference': user.account_reference,
        'region': user.region,
        'plan': profile.current_plan.name,
        'current_balance': str(profile.current_balance),
        'data_used_gb': str(profile.data_used_gb),
        'monthly_data_allowance_gb': profile.current_plan.data_allowance_gb,
        'last_payment_amount': str(profile.last_payment_amount),
        'last_payment_date': profile.last_payment_date.isoformat() if profile.last_payment_date else None,
        'open_complaints': complaint_summary,
        'active_faults': faults,
    }


def generate_chat_response(user, user_message):
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return 'Groq API key is not configured. Please add GROQ_API_KEY to your .env file.'

    context = build_customer_context(user)
    history = list(ChatMessage.objects.filter(user=user).order_by('-created_at')[:8])
    history.reverse()

    client = Groq(api_key=api_key)
    messages = [{'role': 'system', 'content': SYSTEM_PROMPT + f'\n\nCustomer context: {context}'}]
    for item in history:
        messages.append({'role': item.role, 'content': item.content})
    messages.append({'role': 'user', 'content': user_message})

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2,
    )
    return completion.choices[0].message.content
