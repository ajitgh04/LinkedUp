from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from notifications.models import Notification

from .models import Comment, Like, Post


class FeedFlowTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author", email="author@example.com", password="a-strong-password-62"
        )
        self.viewer = User.objects.create_user(
            username="viewer", email="viewer@example.com", password="a-strong-password-62"
        )
        self.post = Post.objects.create(author=self.author, content="A new idea")
        self.client.force_login(self.viewer)

    def test_feed_and_post_interactions(self):
        self.assertEqual(self.client.get(reverse("feed")).status_code, 200)
        self.client.post(reverse("toggle-like", args=[self.post.pk]))
        self.assertTrue(Like.objects.filter(post=self.post, user=self.viewer).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.author, kind="like").exists())
        self.client.post(
            reverse("add-comment", args=[self.post.pk]), {"content": "Well said."}
        )
        self.assertTrue(Comment.objects.filter(post=self.post, user=self.viewer).exists())
        self.assertEqual(Notification.objects.filter(recipient=self.author).count(), 2)

    def test_member_can_publish_a_post(self):
        response = self.client.post(reverse("feed"), {"content": "Hello, community!"})
        self.assertRedirects(response, reverse("feed"))
        self.assertTrue(
            Post.objects.filter(author=self.viewer, content="Hello, community!").exists()
        )
