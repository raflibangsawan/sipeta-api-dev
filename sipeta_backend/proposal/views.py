import json

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
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
    ProposalUpdateBerkasProposalForm,
)
from sipeta_backend.proposal.models import AdministrasiProposal, Proposal
from sipeta_backend.proposal.permissions import IsProposalUsers
from sipeta_backend.proposal.serializers import (
    InteraksiProposalSerializer,
    ProposalDownloadListSerializer,
    ProposalListSerializer,
    ProposalSerializer,
)
from sipeta_backend.proposal.validators import (
    validate_dosen_pembimbings_count,
    validate_dosen_pembimbings_unique,
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
                status=HTTP_400_BAD_REQUEST,
            )

        form = ProposalCreationForm(request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(user=request.user)
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
                "num_pages": paginator.paginator.num_pages,
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


class ProposalChangeStatusView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsDosenTa)

    @property
    def proposal(self):
        if not hasattr(self, "_proposal"):
            self._proposal = Proposal.objects.get(id_proposal=self.kwargs["id"])
        return self._proposal

    def patch(self, request, *args, **kwargs):
        status = request.POST.get("status")
        if status == self.proposal.status:
            return Response(
                {"msg": "Status proposal tidak berubah."}, status=HTTP_400_BAD_REQUEST
            )
        self.proposal.status = status
        self.proposal.save()

        interaction_form = InteraksiProposalChangeStatusForm(data={"content": status})
        interaction = interaction_form.save(proposal=self.proposal, user=request.user)
        serializer = InteraksiProposalSerializer(interaction)
        return Response(serializer.data, status=HTTP_200_OK)


class ProposalChangeDosenPembimbingView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsDosenTa)

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

    def patch(self, request, *args, **kwargs):
        list_dosen_pembimbing = json.loads(request.POST.get("list_dosen_pembimbing"))
        dosen_pembimbings = [
            User.objects.get(id_user=id_dosen_pembimbing)
            for id_dosen_pembimbing in list_dosen_pembimbing
        ]

        msgs, valid_all = [], True
        msg, valid = validate_dosen_pembimbings_unique(dosen_pembimbings)
        if not valid:
            valid_all = False
            msgs.append(msg)

        msg, valid = validate_dosen_pembimbings_count(dosen_pembimbings)
        if not valid:
            valid_all = False
            msgs.append(msg)

        if not valid_all:
            return Response({"msg": msgs}, status=HTTP_400_BAD_REQUEST)

        if set(dosen_pembimbings) == set(self.proposal.dosen_pembimbings.all()):
            return Response(
                {"msg": "Dosen pembimbing tidak berubah."}, status=HTTP_400_BAD_REQUEST
            )

        self.proposal.dosen_pembimbings.set(dosen_pembimbings)
        self.proposal.save()

        interaction_form = InteraksiProposalChangeDosenPembimbingForm(
            data={"content": self.__convert_dosen_pembimbing_to_str(dosen_pembimbings)}
        )
        interaction = interaction_form.save(proposal=self.proposal, user=request.user)
        serializer = InteraksiProposalSerializer(interaction)
        return Response(serializer.data, status=HTTP_200_OK)


class ProposalEditView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsProposalUsers,
        IsMahasiswa | IsDosenTa,
    )

    @property
    def proposal(self):
        if not hasattr(self, "_proposal"):
            self._proposal = Proposal.objects.get(id_proposal=self.kwargs["id"])
        return self._proposal

    def __edit_title(
        self,
        request,
    ):
        title = request.POST.get("title")
        if title == self.proposal.title or title is None:
            return ({}, False)
        self.proposal.title = title
        self.proposal.save()

        interaction_form = InteraksiProposalEditJudulForm(data={"content": title})
        interaction = interaction_form.save(proposal=self.proposal, user=request.user)
        serializer = InteraksiProposalSerializer(interaction)
        return (serializer.data, True)

    def __edit_berkas_proposal(self, request):
        berkas_proposal = request.FILES.get("berkas_proposal")
        if berkas_proposal is None:
            return ({}, False)
        form = ProposalUpdateBerkasProposalForm(
            instance=self.proposal, files=request.FILES
        )
        if not form.is_valid():
            return (form.errors, False)
        form.save()

        interaction_form = InteraksiProposalEditBerkasProposalForm(
            data={"content": berkas_proposal.name}
        )
        interaction = interaction_form.save(proposal=self.proposal, user=request.user)
        serializer = InteraksiProposalSerializer(interaction)
        return (serializer.data, True)

    def patch(self, request, *args, **kwargs):
        # only Dosen TA can edit after pengajuan proposal is closed/proposal is reviewed
        if request.user.role_pengguna == ROLE_MAHASISWA:
            if not AdministrasiProposal._get_status_pengajuan_proposal():
                return Response(
                    {
                        "msg": "Pengajuan proposal sedang ditutup, tidak dapat mengubah status proposal."
                    },
                    status=HTTP_400_BAD_REQUEST,
                )
            if self.proposal.status != PROPOSAL_STATUS_PENDING:
                return Response(
                    {
                        "msg": "Proposal sudah direview oleh Dosen TA, tidak dapat mengubah status proposal."
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

        data_title, status_title = self.__edit_title(request)
        data_berkas, status_berkas = self.__edit_berkas_proposal(request)

        if not status_title and not status_berkas:
            return Response(
                {"msg": "Data proposal tidak berubah."}, status=HTTP_400_BAD_REQUEST
            )
        data = []
        if status_title:
            data.append(data_title)
        if status_berkas:
            data.append(data_berkas)
        return Response(data, status=HTTP_200_OK)


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
