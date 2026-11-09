from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification

from .models import Connection

User = get_user_model()


@login_required
def connections(request):
    incoming = Connection.objects.filter(
        receiver=request.user, status="pending"
    ).select_related("sender")
    outgoing_ids = Connection.objects.filter(
        sender=request.user
    ).values_list("receiver_id", flat=True)
    incoming_ids = Connection.objects.filter(
        receiver=request.user
    ).values_list("sender_id", flat=True)
    suggestions = User.objects.exclude(pk=request.user.pk).exclude(
        pk__in=outgoing_ids
    ).exclude(pk__in=incoming_ids)[:8]
    accepted = Connection.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user), status="accepted"
    ).select_related("sender", "receiver")
    return render(
        request,
        "connections/connections.html",
        {"incoming": incoming, "suggestions": suggestions, "accepted": accepted},
    )


@login_required
def connection_action(request, user_id, action):
    if request.method != "POST":
        return redirect("connections")
    person = get_object_or_404(User, pk=user_id)
    if person == request.user:
        messages.error(request, "You cannot connect with yourself.")
        return redirect("connections")

    outgoing = Connection.objects.filter(sender=request.user, receiver=person)
    incoming = Connection.objects.filter(sender=person, receiver=request.user)
    if action == "connect":
        if incoming.filter(status="pending").exists():
            messages.info(request, "This person has already sent you a request.")
        elif not outgoing.filter(status="pending").exists():
            connection = outgoing.first()
            if connection:
                connection.status = "pending"
                connection.save(update_fields=["status"])
            else:
                Connection.objects.create(sender=request.user, receiver=person)
            Notification.objects.create(
                recipient=person,
                actor=request.user,
                kind="connection",
                message=f"{request.user.get_full_name() or request.user.username} sent you a connection request.",
                url="/connections/",
            )
            messages.success(request, "Connection request sent.")
    elif action == "accept":
        request_obj = get_object_or_404(incoming, status="pending")
        request_obj.status = "accepted"
        request_obj.save(update_fields=["status"])
        Notification.objects.create(
            recipient=person,
            actor=request.user,
            kind="connection",
            message=f"{request.user.get_full_name() or request.user.username} accepted your connection request.",
            url="/connections/",
        )
        messages.success(request, "You are now connected.")
    elif action in ("decline", "cancel"):
        target = incoming if action == "decline" else outgoing
        target.filter(status="pending").delete()
    return redirect("connections")
