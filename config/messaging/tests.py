from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from notifications.models import Notification

from .models import Conversation, Message


class MessagingFlowTests(TestCase):
    def setUp(self):
        self.alex = User.objects.create_user(
            username="alex", email="alex@example.com", password="a-strong-password-62"
        )
        self.jamie = User.objects.create_user(
            username="jamie", email="jamie@example.com", password="a-strong-password-62"
        )
        self.client.force_login(self.alex)

    def test_private_conversation_and_notification(self):
        response = self.client.post(
            reverse("conversation", args=[self.jamie.pk]),
            {"content": "Hello, Jamie."},
        )
        self.assertRedirects(response, reverse("conversation", args=[self.jamie.pk]))
        thread = Conversation.objects.get()
        message = Message.objects.get(conversation=thread)
        self.assertEqual(message.sender, self.alex)
        self.assertTrue(
            Notification.objects.filter(recipient=self.jamie, kind="message").exists()
        )
        self.assertEqual(
            self.client.get(reverse("conversation", args=[self.jamie.pk])).status_code,
            200,
        )
        response = self.client.get(
            reverse("conversation", args=[self.jamie.pk]), {"format": "json"}
        )
        self.assertEqual(response.json()["messages"][0]["content"], "Hello, Jamie.")

    def test_inbox_and_search_render(self):
        self.assertEqual(self.client.get(reverse("inbox")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("search"), {"q": "Jamie"}).status_code, 200
        )
