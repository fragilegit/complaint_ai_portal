from django.shortcuts import redirect, render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import ChatMessage
from .services import generate_chat_response


@login_required
def chat_view(request):
    if not request.user.is_customer:
        messages.error(request, 'Only customers can use the chatbot.')
        return redirect('dashboard')

    if request.method == 'POST':
        prompt = request.POST.get('message', '').strip()
        if prompt:
            ChatMessage.objects.create(user=request.user, role='user', content=prompt)
            reply = generate_chat_response(request.user, prompt)
            ChatMessage.objects.create(user=request.user, role='assistant', content=reply)

    history = ChatMessage.objects.filter(user=request.user)
    return render(request, 'chatbot/chat.html', {'history': history})
