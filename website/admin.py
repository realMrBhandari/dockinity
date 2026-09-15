from django.contrib import admin

from .models import ExperimentMetadata


@admin.register(ExperimentMetadata)
class ExperimentMetadataAdmin(admin.ModelAdmin):

    list_display = (
        "experiment_id",
        "user_email",
        "created_at",
        "experiment_status",
        "started_at",
        "completed_at",
    )

    list_filter = ("experiment_status",)

    search_fields = (
        "experiment_id",
        "user_email",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "experiment_id",
        "user_email",
        "created_at",
        "experiment_status",
        "started_at",
        "completed_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
