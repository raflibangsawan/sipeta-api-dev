from django.contrib import admin

from sipeta_backend.pengumuman.models import Pengumuman


@admin.register(Pengumuman)
class PengumumanAdmin(admin.ModelAdmin):
    list_display = (
        "id_pengumuman",
        "title",
        "semester",
        "created_by",
        "created_on",
    )
    search_fields = (
        "id_pengumuman",
        "title",
        "semester",
        "created_by",
        "created_on",
    )
    list_filter = (
        "id_pengumuman",
        "title",
        "semester",
        "created_by",
        "created_on",
    )
    readonly_fields = ("id_pengumuman",)
