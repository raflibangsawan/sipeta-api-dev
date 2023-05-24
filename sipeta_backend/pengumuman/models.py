import os
import secrets
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from sipeta_backend.pengumuman.validators import (
    validate_file_extension,
    validate_file_size,
)
from sipeta_backend.semester.models import Semester
from sipeta_backend.users.models import User


def create_hash_filename(path, filename):
    filename, file_extension = os.path.splitext(filename)
    return os.path.join(path, f"{secrets.token_hex(16)}{file_extension}")


def hash_filename_lampiran(instance, filename):
    path = "pengumuman_files/"
    return create_hash_filename(path, filename)


class Pengumuman(models.Model):
    id_pengumuman = models.UUIDField(_("ID"), default=uuid.uuid4, editable=False)
    semester = models.ForeignKey(
        Semester, null=False, on_delete=models.CASCADE, related_name="+"
    )
    title = models.CharField(max_length=250, null=False)
    content = models.TextField(max_length=2048)
    lampiran = models.FileField(
        upload_to=hash_filename_lampiran,
        null=False,
        validators=[validate_file_size, validate_file_extension],
    )
    nama_lampiran = models.CharField(max_length=250, null=False)

    created_by = models.ForeignKey(
        User, null=False, on_delete=models.CASCADE, related_name="+"
    )
    created_on = models.DateTimeField(auto_now_add=True)
