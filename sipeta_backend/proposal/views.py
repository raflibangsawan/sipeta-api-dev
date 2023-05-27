from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
from rest_framework.views import APIView
from rest_framework_csv.renderers import CSVRenderer

from sipeta_backend.proposal.constants import (
    PROPOSAL_STATUS_DIBATALKAN,
    PROPOSAL_STATUS_DISETUJUI,
    PROPOSAL_STATUS_PENDING,
)
from sipeta_backend.proposal.filters import ProposalFilter
from sipeta_backend.proposal.forms import (
    InteraksiProposalChangeDosenPembimbingForm,
    InteraksiProposalChangeStatusForm,
    InteraksiProposalCommentForm,
    InteraksiProposalEditBerkasProposalForm,
    InteraksiProposalEditJudulForm,
    ProposalCreationForm,
    ProposalUpdateForm,
)
from sipeta_backend.proposal.models import AdministrasiProposal, Proposal
from sipeta_backend.proposal.permissions import IsProposalUsers
from sipeta_backend.proposal.serializers import (
    InteraksiProposalSerializer,
    ProposalDownloadListSerializer,
    ProposalListSerializer,
    ProposalSerializer,
)
from sipeta_backend.semester.models import Semester
from sipeta_backend.users.constants import ROLE_DOSEN, ROLE_MAHASISWA
from sipeta_backend.users.permissions import (
    IsDosenFasilkom,
    IsDosenTa,
    IsMahasiswa,
    IsMethodReadOnly,
    IsNotEksternal,
)
from sipeta_backend.utils.pagination import Pagination
from sipeta_backend.utils.string import to_bool

User = get_user_model()


class ProposalView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsMahasiswa | IsMethodReadOnly,
    )

    def post(self, request):
        if not AdministrasiProposal._get_status_pengajuan_proposal():
            return Response(
                {"msg": "Pengajuan proposal sedang ditutup"},
                status=HTTP_403_FORBIDDEN,
            )

        form = ProposalCreationForm(request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(user=request.user, is_new_berkas_proposal=True)
            return Response({"id": proposal.id_proposal}, status=HTTP_201_CREATED)
        return Response(form.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request):
        active_semester = Semester._get_active_semester()
        proposals = Proposal.objects.filter(
            Q(semester=active_semester) | Q(status=PROPOSAL_STATUS_DISETUJUI)
        )

        if request.user.role_pengguna == ROLE_DOSEN and request.user.is_dosen_eksternal:
            proposals = proposals.filter(
                dosen_pembimbings__in=[request.user]
            ).distinct()

        # proposal list search feature
        src = request.GET.get("src", None)
        if src:
            if not src.isdigit():
                src = ".*" + src.replace(" ", ".*") + ".*"
            else:
                src = "^" + src
            proposals = proposals.filter(
                Q(title__iregex=src)
                | Q(mahasiswas__name__iregex=src)
                | Q(dosen_pembimbings__name__iregex=src)
                | Q(mahasiswas__kode_identitas__iregex=src)
                | Q(dosen_pembimbings__kode_identitas__iregex=src)
            ).distinct()

        # proposal list filter feature
        proposals = ProposalFilter.filter(proposals, **(request.GET.dict()))

        # proposal list pagination feature
        paginator = Pagination(
            proposals, request.GET.get("page"), request.GET.get("per_page")
        )
        proposals, paginator = paginator.get_content()

        serializer = ProposalListSerializer(proposals, many=True)
        return Response(
            {
                "status_pengajuan_proposal": AdministrasiProposal._get_status_pengajuan_proposal(),
                "page_range": paginator.paginator.get_elided_page_range(
                    paginator.number, on_each_side=2, on_ends=1
                ),
                "proposals": serializer.data,
            },
            status=HTTP_200_OK,
        )


class ProposalChangeStatusPengajuanView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsDosenTa,
    )

    def post(self, request):
        status = request.data.get("status")
        AdministrasiProposal._set_status_pengajuan_proposal(status)

        return Response(
            {"msg": "Status pengajuan proposal berhasil diubah."}, status=HTTP_200_OK
        )


class ProposalDetailView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsProposalUsers | IsNotEksternal,
        IsProposalUsers
        | IsDosenTa
        | IsMethodReadOnly,  # method post only for dosen ta or proposal users
    )

    @property
    def proposal(self):
        if not hasattr(self, "_proposal"):
            self._proposal = Proposal.objects.get(id_proposal=self.kwargs["id"])
        return self._proposal

    def __convert_dosen_pembimbing_to_str(self, dosen_pembimbings):
        if len(dosen_pembimbings) == 0:
            return "tidak ada dosen pembimbing"
        elif len(dosen_pembimbings) == 1:
            return dosen_pembimbings[0].name
        else:
            return dosen_pembimbings[0].name + " dan " + dosen_pembimbings[1].name

    def get(self, request, *args, **kwargs):
        serializer = ProposalSerializer(self.proposal)
        is_mahasiswa_anggota = self.proposal.mahasiswas.filter(
            id=request.user.id
        ).exists()
        is_dosen_tertarik = self.proposal.dosen_tertariks.filter(
            id=request.user.id
        ).exists()
        return Response(
            {
                "proposal": serializer.data,
                "is_mahasiswa_anggota": is_mahasiswa_anggota,
                "is_dosen_tertarik": is_dosen_tertarik,
            },
            status=HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        form = InteraksiProposalCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(proposal=self.proposal, user=request.user)
            serializer = InteraksiProposalSerializer(comment)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(form.errors, status=HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        if request.user.role_pengguna == ROLE_DOSEN and not request.user.is_dosen_ta:
            return Response(
                {"msg": "Dosen pembimbing tidak dapat mengubah proposal."},
                status=HTTP_403_FORBIDDEN,
            )

        if request.user.role_pengguna == ROLE_MAHASISWA:
            if not AdministrasiProposal._get_status_pengajuan_proposal():
                return Response(
                    {
                        "msg": "Pengajuan proposal sedang ditutup, tidak dapat mengubah proposal."
                    },
                    status=HTTP_403_FORBIDDEN,
                )
            if self.proposal.status != PROPOSAL_STATUS_PENDING:
                return Response(
                    {
                        "msg": "Proposal sudah direview oleh Dosen TA, tidak dapat mengubah proposal."
                    },
                    status=HTTP_403_FORBIDDEN,
                )

        proposal_old = {
            "title": self.proposal.title,
            "status": self.proposal.status,
            "sumber_ide": self.proposal.sumber_ide,
            "berkas_proposal": self.proposal.berkas_proposal,
            "mahasiswas": self.proposal.mahasiswas.all(),
            "dosen_pembimbings": self.proposal.dosen_pembimbings.all(),
        }

        form = ProposalUpdateForm(request.POST, request.FILES, instance=self.proposal)
        if form.is_valid():
            errors = []

            # none editable fields should not change
            if form.cleaned_data["sumber_ide"] != proposal_old["sumber_ide"]:
                errors.append("Tidak dapat mengubah sumber ide")
            if set(form.cleaned_data["mahasiswas"]) != set(proposal_old["mahasiswas"]):
                errors.append("Tidak dapat mengubah mahasiswa")
            if request.user.role_pengguna == ROLE_MAHASISWA:
                # only dosen ta can change status and dosen pembimbing
                if form.cleaned_data["status"] != proposal_old["status"]:
                    errors.append("Mahasiswa tidak dapat mengubah status")
                if list(form.cleaned_data["dosen_pembimbings"]) != list(
                    proposal_old["dosen_pembimbings"]
                ):
                    errors.append("Mahasiswa tidak dapat mengubah dosen pembimbing")

            if errors:
                return Response(
                    {"msg": "Proposal gagal diubah.", "errors": errors},
                    status=HTTP_400_BAD_REQUEST,
                )

            interactions = []

            is_new_berkas_proposal = False
            if form.cleaned_data["title"] != proposal_old["title"]:
                interaction_form = InteraksiProposalEditJudulForm(
                    data={"content": form.cleaned_data["title"]}
                )
                interaction = interaction_form.save(
                    proposal=self.proposal, user=request.user
                )
                interactions.append(interaction)

            if form.cleaned_data["status"] != proposal_old["status"]:
                interaction_form = InteraksiProposalChangeStatusForm(
                    data={"content": form.cleaned_data["status"]}
                )
                interaction = interaction_form.save(
                    proposal=self.proposal, user=request.user
                )
                interactions.append(interaction)

            if form.cleaned_data["berkas_proposal"] != proposal_old["berkas_proposal"]:
                is_new_berkas_proposal = True
                interaction_form = InteraksiProposalEditBerkasProposalForm(
                    data={"content": form.cleaned_data["berkas_proposal"].name}
                )
                interaction = interaction_form.save(
                    proposal=self.proposal, user=request.user
                )
                interactions.append(interaction)

            if list(form.cleaned_data["dosen_pembimbings"]) != list(
                proposal_old["dosen_pembimbings"]
            ):
                interaction_form = InteraksiProposalChangeDosenPembimbingForm(
                    data={
                        "content": self.__convert_dosen_pembimbing_to_str(
                            form.cleaned_data["dosen_pembimbings"]
                        )
                    }
                )
                interaction = interaction_form.save(
                    proposal=self.proposal, user=request.user
                )
                interactions.append(interaction)

            form.save(is_new_berkas_proposal=is_new_berkas_proposal)
            serializer = InteraksiProposalSerializer(interactions, many=True)
            return Response(
                {"msg": "Proposal berhasil diubah.", "interactions": serializer.data},
                status=HTTP_200_OK,
            )
        return Response(
            {"msg": "Proposal gagal diubah.", "errors": form.errors},
            status=HTTP_400_BAD_REQUEST,
        )


class ProposalDosenInterestView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsDosenFasilkom)

    @property
    def proposal(self):
        if not hasattr(self, "_proposal"):
            self._proposal = Proposal.objects.get(id_proposal=self.kwargs["id"])
        return self._proposal

    def patch(self, request, *args, **kwargs):
        interest = to_bool(request.POST.get("interest"))
        if (request.user in self.proposal.dosen_tertariks.all()) == interest:
            return Response(
                {"msg": "Interest tidak berubah."}, status=HTTP_400_BAD_REQUEST
            )
        if interest:
            self.proposal.dosen_tertariks.add(request.user)
        else:
            self.proposal.dosen_tertariks.remove(request.user)
        self.proposal.save()

        return Response({"msg": "Interest berhasil diubah."}, status=HTTP_200_OK)


class ProposalCancelView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsProposalUsers, IsMahasiswa)

    @property
    def proposal(self):
        if not hasattr(self, "_proposal"):
            self._proposal = Proposal.objects.get(id_proposal=self.kwargs["id"])
        return self._proposal

    def patch(self, request, *args, **kwargs):
        if self.proposal.status == PROPOSAL_STATUS_DIBATALKAN:
            return Response(
                {"msg": "Proposal sudah dibatalkan."}, status=HTTP_400_BAD_REQUEST
            )
        if not AdministrasiProposal._get_status_pengajuan_proposal():
            return Response(
                {
                    "msg": "Pengajuan proposal sedang ditutup, tidak dapat mengubah status proposal."
                },
                status=HTTP_400_BAD_REQUEST,
            )
        if not self.proposal.status == PROPOSAL_STATUS_PENDING:
            return Response(
                {
                    "msg": "Proposal sudah direview oleh Dosen TA, tidak dapat mengubah status proposal."
                },
                status=HTTP_400_BAD_REQUEST,
            )

        self.proposal.status = PROPOSAL_STATUS_DIBATALKAN
        self.proposal.save()

        interaction_form = InteraksiProposalChangeStatusForm(
            data={"content": PROPOSAL_STATUS_DIBATALKAN}
        )
        interaction = interaction_form.save(proposal=self.proposal, user=request.user)
        serializer = InteraksiProposalSerializer(interaction)
        return Response(serializer.data, status=HTTP_200_OK)


class ProposalDownloadListView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsDosenTa)
    renderer_classes = (CSVRenderer,)

    def get(self, request, *args, **kwargs):
        semester = Semester._get_active_semester()
        proposals = Proposal.objects.filter(
            semester=semester, status=PROPOSAL_STATUS_PENDING
        )
        serializer = ProposalDownloadListSerializer(proposals, many=True)
        response = Response(data=serializer.data, status=HTTP_200_OK)
        response[
            "Content-Disposition"
        ] = f'attachment; filename="Proposal Pending Semester {semester}.csv"'
        return response
