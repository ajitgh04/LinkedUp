import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
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
        response = self.client.get(reverse("jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apply now")
        self.assertNotContains(response, "Attach CV or resume")
        response = self.client.post(reverse("apply-job", args=[self.job.pk]))
        self.assertRedirects(response, reverse("jobs"))
        self.assertTrue(
            JobApplication.objects.filter(
                job=self.job, applicant=self.applicant
            ).exists()
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

    def test_applicant_can_view_their_application_history(self):
        JobApplication.objects.create(job=self.job, applicant=self.applicant)

        response = self.client.get(reverse("my-applications"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job.title)
        self.assertContains(response, self.job.company)

    def test_recruiter_can_view_applicant_and_resume(self):
        application = JobApplication.objects.create(
            job=self.job, applicant=self.applicant
        )
        with tempfile.TemporaryDirectory() as media_directory:
            with override_settings(MEDIA_ROOT=media_directory):
                self.applicant.resume = SimpleUploadedFile(
                    "applicant-cv.pdf",
                    b"resume contents",
                    content_type="application/pdf",
                )
                self.applicant.save()
                self.client.force_login(self.recruiter)

                response = self.client.get(
                    reverse("job-applicants", args=[self.job.pk])
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, self.applicant.username)
                self.assertContains(response, "View CV / resume")

                response = self.client.get(
                    reverse("profile", args=[self.applicant.pk])
                )
                self.assertNotContains(response, "Download CV / resume")

                response = self.client.get(
                    reverse("applicant-resume", args=[application.pk])
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "application/pdf")
                self.assertEqual(
                    b"".join(response.streaming_content), b"resume contents"
                )

    def test_non_recruiter_cannot_view_applicants_or_resume(self):
        application = JobApplication.objects.create(
            job=self.job, applicant=self.applicant
        )

        response = self.client.get(reverse("job-applicants", args=[self.job.pk]))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            reverse("applicant-resume", args=[application.pk])
        )
        self.assertEqual(response.status_code, 404)
