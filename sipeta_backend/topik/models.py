import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from sipeta_backend.topik.constants import (
    KETERSEDIAAN_CHOICES,
    PENGERJAAN_CHOICES,
    SENDIRI,
    TERSEDIA,
)
from sipeta_backend.users.models import User


class Bidang(models.Model):
    name = models.CharField(max_length=250, null=False)
    short = models.CharField(max_length=10, null=False)

    def __str__(self) -> str:
        return self.name


class Topik(models.Model):
    id_topik = models.UUIDField(_("ID"), default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250, null=False)
    ketersediaan = models.CharField(
        max_length=20, null=False, default=TERSEDIA, choices=KETERSEDIAAN_CHOICES
    )
    bidangs = models.ManyToManyField(Bidang, blank=True, related_name="+")
    pengerjaan = models.IntegerField(
        null=False, default=SENDIRI, choices=PENGERJAAN_CHOICES
    )
    content = models.TextField(null=False, max_length=2048)

    created_by = models.ForeignKey(
        User, null=False, on_delete=models.CASCADE, related_name="+"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    deleted_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self) -> str:
        return f"{self.title}"
