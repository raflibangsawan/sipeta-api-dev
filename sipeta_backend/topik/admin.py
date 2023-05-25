from django.contrib import admin

from sipeta_backend.topik.models import Bidang, Topik


@admin.register(Bidang)
class Bidang(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "short",
    )
    search_fields = (
        "id",
        "name",
        "short",
    )
    list_filter = (
        "id",
        "name",
        "short",
    )
    readonly_fields = ("id",)


@admin.register(Topik)
class TopikAdmin(admin.ModelAdmin):
    list_display = (
        "id_topik",
        "title",
        "ketersediaan",
        "pengerjaan",
        "created_by",
        "created_on",
        "deleted_on",
    )
    search_fields = (
        "id_topik",
        "title",
        "ketersediaan",
        "pengerjaan",
    )
    list_filter = (
        "id_topik",
        "title",
        "ketersediaan",
        "pengerjaan",
    )
    readonly_fields = ("id_topik",)
