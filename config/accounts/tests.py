from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountFlowTests(TestCase):
    def test_registration_creates_and_signs_in_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Avery",
                "last_name": "Stone",
                "username": "averystone",
                "email": "avery@example.com",
                "password1": "a-strong-password-62",
                "password2": "a-strong-password-62",
            },
        )
        self.assertRedirects(response, reverse("feed"))
        user = User.objects.get(email="avery@example.com")
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_login_uses_email_address(self):
        User.objects.create_user(
            username="avery", email="avery@example.com", password="a-strong-password-62"
        )
        response = self.client.post(
            reverse("login"),
            {"username": "avery@example.com", "password": "a-strong-password-62"},
        )
        self.assertRedirects(response, reverse("feed"))

    def test_logout_clears_the_authenticated_session(self):
        user = User.objects.create_user(
            username="avery", email="avery@example.com", password="a-strong-password-62"
        )
        self.client.force_login(user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_authenticated_user_can_update_profile(self):
        user = User.objects.create_user(
            username="avery", email="avery@example.com", password="a-strong-password-62"
        )
        self.client.force_login(user)
        response = self.client.post(
            reverse("my-profile"),
            {
                "first_name": "Avery",
                "last_name": "Stone",
                "headline": "Product designer",
                "bio": "Designing thoughtful products.",
                "location": "Portland",
                "website": "https://example.com",
            },
        )
        self.assertRedirects(response, reverse("my-profile"))
        user.refresh_from_db()
        self.assertEqual(user.headline, "Product designer")

    def test_owner_can_add_experience_and_education(self):
        user = User.objects.create_user(
            username="avery", email="avery@example.com", password="a-strong-password-62"
        )
        self.client.force_login(user)
        experience = self.client.post(
            reverse("my-profile"),
            {
                "action": "experience",
                "position": "Designer",
                "company": "Northstar",
                "description": "Building useful products.",
                "start_date": "2022-01-01",
                "currently_working": "on",
            },
        )
        self.assertRedirects(experience, reverse("my-profile"))
        education = self.client.post(
            reverse("my-profile"),
            {
                "action": "education",
                "institution": "State University",
                "degree": "BS",
                "field_of_study": "Design",
                "start_year": 2018,
                "end_year": 2022,
            },
        )
        self.assertRedirects(education, reverse("my-profile"))
        self.assertEqual(user.experiences.count(), 1)
        self.assertEqual(user.education.count(), 1)
