import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="resume",
            field=models.FileField(
                blank=True,
                help_text="PDF, DOC, or DOCX",
                upload_to="resumes/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["pdf", "doc", "docx"]
                    )
                ],
                verbose_name="CV or resume",
            ),
        ),
    ]
