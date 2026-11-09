from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from notifications.models import Notification


class ConnectionFlowTests(TestCase):
    def setUp(self):
        self.alex = User.objects.create_user(
            username="alex", email="alex@example.com", password="a-strong-password-62"
        )
        self.jamie = User.objects.create_user(
            username="jamie", email="jamie@example.com", password="a-strong-password-62"
        )

    def test_request_can_be_accepted_and_notifies_sender(self):
        self.client.force_login(self.alex)
        response = self.client.post(
            reverse("connection-action", args=[self.jamie.pk, "connect"])
        )
        self.assertRedirects(response, reverse("connections"))
        self.assertTrue(Notification.objects.filter(recipient=self.jamie).exists())

        self.client.force_login(self.jamie)
        self.client.post(reverse("connection-action", args=[self.alex.pk, "accept"]))
        self.assertTrue(
            self.alex.sent_connections.filter(receiver=self.jamie, status="accepted").exists()
        )
        self.assertEqual(self.alex.notifications.count(), 1)

    def test_member_can_render_network_and_profile_pages(self):
        self.client.force_login(self.alex)
        self.assertEqual(self.client.get(reverse("connections")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("profile", args=[self.jamie.pk])).status_code, 200
        )
