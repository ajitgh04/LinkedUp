from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Job, JobApplication


class JobFlowTests(TestCase):
    def setUp(self):
        self.recruiter = User.objects.create_user(
            username="recruiter", email="recruiter@example.com", password="a-strong-password-62"
        )
        self.applicant = User.objects.create_user(
            username="applicant", email="applicant@example.com", password="a-strong-password-62"
        )
        self.job = Job.objects.create(
            recruiter=self.recruiter,
            title="Product designer",
            company="Northstar",
            location="Remote",
            description="Build useful things.",
        )
        self.client.force_login(self.applicant)

    def test_job_listing_and_application(self):
        self.assertEqual(self.client.get(reverse("jobs")).status_code, 200)
        response = self.client.post(
            reverse("apply-job", args=[self.job.pk]),
            {
                "resume": SimpleUploadedFile(
                    "resume.pdf", b"sample resume", content_type="application/pdf"
                )
            },
        )
        self.assertRedirects(response, reverse("jobs"))
        self.assertTrue(
            JobApplication.objects.filter(job=self.job, applicant=self.applicant).exists()
        )

    def test_recruiter_can_publish_job(self):
        self.client.force_login(self.recruiter)
        response = self.client.post(
            reverse("create-job"),
            {
                "title": "Engineer",
                "company": "Northstar",
                "location": "Remote",
                "salary": "Competitive",
                "description": "Build software.",
            },
        )
        self.assertRedirects(response, reverse("jobs"))
        self.assertTrue(Job.objects.filter(title="Engineer").exists())
