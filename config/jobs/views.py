from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Job, JobApplication


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ("title", "company", "location", "salary", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ("resume",)


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
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Your application has been submitted.")
        else:
            messages.error(request, "Please attach your resume to apply.")
    return redirect("jobs")
