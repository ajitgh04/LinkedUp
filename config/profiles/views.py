from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import ProfileForm
from connections.models import Connection
from .models import Education, Experience
from django import forms

User = get_user_model()


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = (
            "position",
            "company",
            "description",
            "start_date",
            "end_date",
            "currently_working",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ("institution", "degree", "field_of_study", "start_year", "end_year")


@login_required
def my_profile(request):
    if request.method == "POST":
        if request.POST.get("action") == "experience":
            experience_form = ExperienceForm(request.POST)
            if experience_form.is_valid():
                experience = experience_form.save(commit=False)
                experience.user = request.user
                experience.save()
                return redirect("my-profile")
            form = ProfileForm(instance=request.user)
            education_form = EducationForm()
        elif request.POST.get("action") == "education":
            education_form = EducationForm(request.POST)
            if education_form.is_valid():
                education = education_form.save(commit=False)
                education.user = request.user
                education.save()
                return redirect("my-profile")
            form = ProfileForm(instance=request.user)
            experience_form = ExperienceForm()
        else:
            form = ProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect("my-profile")
            experience_form = ExperienceForm()
            education_form = EducationForm()
    else:
        form = ProfileForm(instance=request.user)
        experience_form = ExperienceForm()
        education_form = EducationForm()
    return render(
        request,
        "profiles/profile.html",
        {
            "profile_user": request.user,
            "form": form,
            "experience_form": experience_form,
            "education_form": education_form,
            "is_owner": True,
        },
    )


@login_required
def profile_detail(request, user_id):
    person = get_object_or_404(User, pk=user_id)
    if person == request.user:
        return redirect("my-profile")
    connection = Connection.objects.filter(
        Q(sender=request.user, receiver=person)
        | Q(sender=person, receiver=request.user)
    ).first()
    return render(
        request,
        "profiles/profile.html",
        {
            "profile_user": person,
            "connection": connection,
            "is_owner": False,
        },
    )


@login_required
def search(request):
    query = request.GET.get("q", "").strip()
    people = User.objects.none()
    jobs = []
    posts = []
    if query:
        people = User.objects.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(username__icontains=query)
            | Q(headline__icontains=query)
            | Q(location__icontains=query)
        ).exclude(pk=request.user.pk)[:8]
        from jobs.models import Job
        from posts.models import Post

        jobs = Job.objects.filter(
            Q(title__icontains=query)
            | Q(company__icontains=query)
            | Q(location__icontains=query)
        ).select_related("recruiter")[:6]
        posts = Post.objects.filter(content__icontains=query).select_related(
            "author"
        )[:6]
    return render(
        request,
        "profiles/search.html",
        {"query": query, "people": people, "jobs": jobs, "posts": posts},
    )
