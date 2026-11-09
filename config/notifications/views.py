from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Notification


@login_required
def notification_list(request):
    if request.method == "POST":
        Notification.objects.filter(
            recipient=request.user, read_at__isnull=True
        ).update(read_at=timezone.now())
        return redirect("notifications")
    notifications = Notification.objects.filter(recipient=request.user)
    notifications.filter(read_at__isnull=True).update(read_at=timezone.now())
    notifications = notifications.select_related("actor")[:40]
    return render(
        request, "notifications/list.html", {"notifications": notifications}
    )
