from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Notification


class NotificationFlowTests(TestCase):
    def test_notifications_can_be_marked_as_read(self):
        user = User.objects.create_user(
            username="member", email="member@example.com", password="a-strong-password-62"
        )
        notification = Notification.objects.create(
            recipient=user, kind="connection", message="A new connection request."
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("notifications")).status_code, 200)
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)
