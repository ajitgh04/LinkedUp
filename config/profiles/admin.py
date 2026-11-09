from django.contrib import admin

from .models import Education, Experience


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("user", "position", "company", "start_date", "currently_working")
    search_fields = ("user__email", "company", "position")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "degree", "start_year", "end_year")
    search_fields = ("user__email", "institution", "degree")
