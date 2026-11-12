import mimetypes
import os

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from .models import Job, JobApplication


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ("title", "company", "location", "salary", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}


@login_required
def job_list(request):
    jobs = Job.objects.select_related("recruiter").prefetch_related("applications")[:30]
    applied_ids = set(
        JobApplication.objects.filter(applicant=request.user).values_list(
            "job_id", flat=True
        )
    )
    return render(
        request,
        "jobs/jobs.html",
        {"jobs": jobs, "applied_ids": applied_ids},
    )


@login_required
def create_job(request):
    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.recruiter = request.user
        job.save()
        messages.success(request, "Your job listing has been published.")
        return redirect("jobs")
    return render(request, "jobs/create.html", {"form": form})


@login_required
def apply_to_job(request, job_id):
    if request.method != "POST":
        return redirect("jobs")
    job = get_object_or_404(Job, pk=job_id)
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, "You have already applied for this role.")
    else:
        JobApplication.objects.create(job=job, applicant=request.user)
        messages.success(request, "Your application has been submitted.")
    return redirect("jobs")


@login_required
def my_applications(request):
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related("job", "job__recruiter").order_by("-applied_at")
    return render(
        request,
        "jobs/my_applications.html",
        {"applications": applications},
    )


@login_required
def job_applicants(request, job_id):
    job = get_object_or_404(Job, pk=job_id, recruiter=request.user)
    applications = job.applications.select_related("applicant").order_by(
        "-applied_at"
    )
    return render(
        request,
        "jobs/applicants.html",
        {"job": job, "applications": applications},
    )


@login_required
def applicant_resume(request, application_id):
    application = get_object_or_404(
        JobApplication.objects.select_related("applicant"),
        pk=application_id,
        job__recruiter=request.user,
    )
    resume = application.applicant.resume
    if not resume:
        raise Http404("This applicant has not added a CV or resume.")

    content_type = mimetypes.guess_type(resume.name)[0] or "application/octet-stream"
    return FileResponse(
        resume.open("rb"),
        as_attachment=False,
        filename=os.path.basename(resume.name),
        content_type=content_type,
    )
