from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from notifications.models import Notification

from .models import Conversation, Message

User = get_user_model()


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        Q(participant_one=request.user) | Q(participant_two=request.user)
    ).prefetch_related("messages")
    threads = [
        {
            "conversation": thread,
            "person": thread.other_participant(request.user),
            "last_message": thread.messages.last(),
        }
        for thread in conversations
    ]
    return render(
        request,
        "messaging/inbox.html",
        {"threads": threads},
    )


@login_required
def conversation(request, user_id):
    person = get_object_or_404(User, pk=user_id)
    if person == request.user:
        messages.error(request, "Choose another member to start a conversation.")
        return redirect("inbox")
    first, second = sorted((request.user, person), key=lambda user: user.pk)
    thread, _ = Conversation.objects.get_or_create(
        participant_one=first, participant_two=second
    )
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(
                conversation=thread,
                sender=request.user,
                content=content,
            )
            thread.save()
            Notification.objects.create(
                recipient=person,
                actor=request.user,
                kind="message",
                message=f"{request.user.get_full_name() or request.user.username} sent you a message.",
                url=f"/messages/{request.user.pk}/",
            )
            return redirect("conversation", user_id=person.pk)
        messages.error(request, "Write a message before sending it.")
    thread.messages.filter(read_at__isnull=True).exclude(sender=request.user).update(
        read_at=timezone.now()
    )
    thread_messages = thread.messages.select_related("sender")
    if request.GET.get("format") == "json":
        return JsonResponse(
            {
                "messages": [
                    {
                        "id": item.pk,
                        "sender": item.sender.get_full_name() or item.sender.username,
                        "content": item.content,
                        "created_at": item.created_at.isoformat(),
                        "mine": item.sender_id == request.user.pk,
                        "avatar": (
                            item.sender.profile_picture.url
                            if item.sender.profile_picture
                            else ""
                        ),
                        "initial": (
                            item.sender.first_name or item.sender.username
                        )[:1].upper(),
                    }
                    for item in thread_messages
                ]
            }
        )
    return render(
        request,
        "messaging/conversation.html",
        {"thread": thread, "person": person, "thread_messages": thread_messages},
    )
