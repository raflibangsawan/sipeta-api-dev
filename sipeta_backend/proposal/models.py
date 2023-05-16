import os
import secrets
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from sipeta_backend.proposal.constants import (
    INTERAKSI_PROPOSAL_TIPE_CHOICES,
    PROPOSAL_STATUS_CHOICES,
    PROPOSAL_STATUS_PENDING,
    PROPOSAL_SUMBER_IDE_CHOICES,
    PROPOSAL_SUMBER_IDE_MAHASISWA,
)
from sipeta_backend.proposal.validators import (
    validate_file_extension,
    validate_file_size,
)
from sipeta_backend.semester.models import Semester
from sipeta_backend.users.models import User
from sipeta_backend.utils.string import to_bool


def create_hash_filename(path, filename):
    filename, file_extension = os.path.splitext(filename)
    return os.path.join(path, f"{secrets.token_hex(16)}{file_extension}")


def hash_filename_presentasi(instance, filename):
    path = "proposal_files/"
    return create_hash_filename(path, filename)


class Proposal(models.Model):
    id_proposal = models.UUIDField(_("ID"), default=uuid.uuid4, editable=False)
    semester = models.ForeignKey(
        Semester, null=False, on_delete=models.CASCADE, related_name="+"
    )
    title = models.CharField(max_length=250, null=False)
    sumber_ide = models.CharField(
        max_length=10,
        null=True,
        default=PROPOSAL_SUMBER_IDE_MAHASISWA,
        choices=PROPOSAL_SUMBER_IDE_CHOICES,
    )
    status = models.CharField(
        max_length=20,
        null=False,
        default=PROPOSAL_STATUS_PENDING,
        choices=PROPOSAL_STATUS_CHOICES,
    )
    berkas_proposal = models.FileField(
        upload_to=hash_filename_presentasi,
        null=False,
        validators=[validate_file_size, validate_file_extension],
    )
    nama_berkas_proposal = models.CharField(max_length=250, null=False)

    mahasiswas = models.ManyToManyField(
        User, blank=False, related_name="%(class)s_mahasiswa"
    )
    dosen_pembimbings = models.ManyToManyField(
        User, blank=True, related_name="%(class)s_pembimbing"
    )

    dosen_tertariks = models.ManyToManyField(
        User, blank=True, related_name="%(class)s_tertarik"
    )

    created_by = models.ForeignKey(
        User, null=False, on_delete=models.CASCADE, related_name="+"
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["semester", "-created_on"]

    def __str__(self) -> str:
        return f"{self.title}"

    @property
    def interaksi_proposals(self):
        return InteraksiProposal.objects.filter(proposal=self)


class AdministrasiProposal(models.Model):
    status_pengajuan_proposal = models.BooleanField(
        blank=False, null=False, default=True
    )

    @staticmethod
    def _get_status_pengajuan_proposal():
        return AdministrasiProposal.objects.first().status_pengajuan_proposal

    @staticmethod
    def _set_status_pengajuan_proposal(status):
        if AdministrasiProposal.objects.count() == 0:
            administrasi_proposal = AdministrasiProposal.objects.create()
        else:
            administrasi_proposal = AdministrasiProposal.objects.first()
        administrasi_proposal.status_pengajuan_proposal = to_bool(status)
        administrasi_proposal.save()


class InteraksiProposal(models.Model):
    proposal = models.ForeignKey(Proposal, blank=False, on_delete=models.CASCADE)
    tipe = models.CharField(
        max_length=3, blank=False, choices=INTERAKSI_PROPOSAL_TIPE_CHOICES
    )
    content = models.TextField(blank=False)

    created_by = models.ForeignKey(
        User, null=False, on_delete=models.CASCADE, related_name="+"
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_on"]
