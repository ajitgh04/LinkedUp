from django.contrib import admin

from .models import Comment, Like, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("author__email", "content")


admin.site.register((Comment, Like))
