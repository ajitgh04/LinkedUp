from django.contrib import admin

from .models import Job, JobApplication

admin.site.site_title = "LinkedIn Clone Admin"
admin.site.site_header = "LinkedIn Clone Admin"
admin.site.index_title = "Admin Dashboard"


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "recruiter", "created_at")
    list_filter = ("created_at", "location")
    search_fields = ("title", "company", "recruiter__email")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "applied_at")
    list_filter = ("status", "applied_at")
    search_fields = ("job__title", "applicant__email")
