from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("participant_one", "participant_two", "updated_at")
    search_fields = ("participant_one__email", "participant_two__email")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "conversation", "created_at", "read_at")
    search_fields = ("sender__email", "content")
