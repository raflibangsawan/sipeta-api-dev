from django.contrib import admin

from sipeta_backend.proposal.models import Proposal


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        "id_proposal",
        "title",
        "semester",
        "status",
        "created_by",
        "created_on",
    )
    search_fields = (
        "id_proposal",
        "title",
        "semester",
        "status",
        "created_by",
        "created_on",
    )
    list_filter = (
        "id_proposal",
        "title",
        "semester",
        "status",
        "created_by",
        "created_on",
    )
    readonly_fields = ("id_proposal",)
