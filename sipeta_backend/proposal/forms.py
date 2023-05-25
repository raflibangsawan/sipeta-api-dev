import json

from django import forms
from django.contrib.auth import get_user_model

from sipeta_backend.proposal.constants import (
    INTERAKSI_PROPOSAL_TIPE_CHANGE_DOSEN_PEMBIMBING,
    INTERAKSI_PROPOSAL_TIPE_CHANGE_STATUS_PROPOSAL,
    INTERAKSI_PROPOSAL_TIPE_EDIT_BERKAS_PROPOSAL,
    INTERAKSI_PROPOSAL_TIPE_EDIT_JUDUL_PROPOSAL,
    INTERAKSI_PROPOSAL_TIPE_KOMENTAR,
    PROPOSAL_STATUS_PENDING,
)
from sipeta_backend.proposal.models import InteraksiProposal, Proposal
from sipeta_backend.proposal.validators import (
    validate_dosen_pembimbings_count,
    validate_dosen_pembimbings_unique,
    validate_mahasiswas_count,
    validate_mahasiswas_unique,
)
from sipeta_backend.semester.models import Semester

User = get_user_model()


class ProposalCreationForm(forms.ModelForm):
    list_mahasiswa = forms.CharField(max_length=255, required=True)
    list_dosen_pembimbing = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Proposal
        fields = [
            "title",
            "sumber_ide",
            "berkas_proposal",
            "list_mahasiswa",
            "list_dosen_pembimbing",
        ]

    def save(self, commit=True, *args, **kwargs):
        proposal = super().save(commit=False)
        proposal.semester = Semester._get_active_semester()
        if not kwargs.get("editing"):
            proposal.status = PROPOSAL_STATUS_PENDING
        if kwargs.get("is_new_berkas_proposal"):
            proposal.nama_berkas_proposal = self.cleaned_data["berkas_proposal"].name
        if kwargs.get("user"):
            proposal.created_by = kwargs.get("user")
        if commit:
            proposal.save()
            if not kwargs.get("editing"):
                proposal.mahasiswas.set(self.cleaned_data["mahasiswas"])
            proposal.dosen_pembimbings.set(self.cleaned_data["dosen_pembimbings"])
        return proposal

    def clean(self):
        cleaned_data = super().clean()

        list_mahasiswa = json.loads(cleaned_data.get("list_mahasiswa"))
        mahasiswas = []
        for id_mahasiswa in list_mahasiswa:
            try:
                mahasiswa = User.objects.get(id_user=id_mahasiswa)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    f"Mahasiswa dengan id {id_mahasiswa} tidak ditemukan"
                )
            mahasiswas.append(mahasiswa)

        list_dosen_pembimbing = json.loads(cleaned_data.get("list_dosen_pembimbing"))
        dosen_pembimbings = []
        for id_dosen_pembimbing in list_dosen_pembimbing:
            try:
                dosen_pembimbing = User.objects.get(id_user=id_dosen_pembimbing)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    f"Dosen dengan id {id_dosen_pembimbing} tidak ditemukan"
                )
            dosen_pembimbings.append(dosen_pembimbing)

        messages, valid_all = [], True

        message, valid = validate_mahasiswas_unique(mahasiswas)
        if not valid:
            valid_all = False
            messages.append(message)

        message, valid = validate_mahasiswas_count(mahasiswas)
        if not valid:
            valid_all = False
            messages.append(message)

        message, valid = validate_dosen_pembimbings_unique(dosen_pembimbings)
        if not valid:
            valid_all = False
            messages.append(message)

        message, valid = validate_dosen_pembimbings_count(dosen_pembimbings)
        if not valid:
            valid_all = False
            messages.append(message)

        if not valid_all:
            raise forms.ValidationError(messages)

        cleaned_data["mahasiswas"] = mahasiswas
        cleaned_data["dosen_pembimbings"] = dosen_pembimbings

        return cleaned_data


class ProposalUpdateForm(ProposalCreationForm):
    class Meta(ProposalCreationForm.Meta):
        fields = ProposalCreationForm.Meta.fields + ["status"]

    def save(self, commit=True, *args, **kwargs):
        return super().save(commit, editing=True, *args, **kwargs)


class AbstractInteraksiProposalForm(forms.ModelForm):
    tipe = None
    template_content = ""

    class Meta:
        model = InteraksiProposal
        fields = ["content"]

    def save(self, commit=True, *args, **kwargs):
        interaksi_proposal = super().save(commit=False)
        interaksi_proposal.tipe = self.tipe
        interaksi_proposal.created_by = kwargs.get("user")
        interaksi_proposal.proposal = kwargs.get("proposal")
        if self.tipe == INTERAKSI_PROPOSAL_TIPE_EDIT_BERKAS_PROPOSAL:
            interaksi_proposal.content = self.template_content.format(
                interaksi_proposal.created_by
            )
        elif self.tipe != INTERAKSI_PROPOSAL_TIPE_KOMENTAR:
            interaksi_proposal.content = self.template_content.format(
                interaksi_proposal.created_by, interaksi_proposal.content
            )
        if commit:
            interaksi_proposal.save()
        return interaksi_proposal


class InteraksiProposalCommentForm(AbstractInteraksiProposalForm):
    tipe = INTERAKSI_PROPOSAL_TIPE_KOMENTAR
    template_content = "{}"


class InteraksiProposalChangeStatusForm(AbstractInteraksiProposalForm):
    tipe = INTERAKSI_PROPOSAL_TIPE_CHANGE_STATUS_PROPOSAL
    template_content = "{} mengubah status proposal menjadi {}"


class InteraksiProposalChangeDosenPembimbingForm(AbstractInteraksiProposalForm):
    tipe = INTERAKSI_PROPOSAL_TIPE_CHANGE_DOSEN_PEMBIMBING
    template_content = "{} mengubah dosen pembimbing menjadi {}"


class InteraksiProposalEditJudulForm(AbstractInteraksiProposalForm):
    tipe = INTERAKSI_PROPOSAL_TIPE_EDIT_JUDUL_PROPOSAL
    template_content = "{} mengubah judul proposal menjadi {}"


class InteraksiProposalEditBerkasProposalForm(AbstractInteraksiProposalForm):
    tipe = INTERAKSI_PROPOSAL_TIPE_EDIT_BERKAS_PROPOSAL
    template_content = "{} mengubah berkas proposal"
