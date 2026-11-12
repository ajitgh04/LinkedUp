from django.conf import settings
from django.db import migrations


def move_existing_resumes_to_profiles(apps, schema_editor):
    JobApplication = apps.get_model("jobs", "JobApplication")
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    seen_applicants = set()

    resumes = JobApplication.objects.exclude(resume="").order_by(
        "applicant_id", "-applied_at", "-pk"
    )
    for applicant_id, resume in resumes.values_list("applicant_id", "resume"):
        if applicant_id in seen_applicants:
            continue
        seen_applicants.add(applicant_id)
        User.objects.filter(pk=applicant_id, resume="").update(resume=resume)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_resume"),
        ("jobs", "0002_validate_resume_extension"),
    ]

    operations = [
        migrations.RunPython(
            move_existing_resumes_to_profiles,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="jobapplication",
            name="resume",
        ),
    ]
