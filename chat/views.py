from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from datetime import datetime,timezone


@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '') 
    users = User.objects.exclude(id=request.user.id) 
    
    # Filter chats between the logged-in user and the specific room_name user
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))  

    chats = chats.order_by('timestamp') 

    user_last_messages = []

    # Populate the user_last_messages list with the last message for each user
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Use `datetime.min.replace(tzinfo=timezone.utc)` for offset-aware consistency
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    return render(request, 'chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query 
    })


@login_required
def start_page(request):
    # Get all users except the current logged-in user
    users = User.objects.exclude(id=request.user.id)

    return render(request, 'home.html', {
        'users': users,
    })