from django.db.models import Q
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from sipeta_backend.proposal.constants import PROPOSAL_STATUS_DITERIMA
from sipeta_backend.proposal.forms import ProposalCreationForm
from sipeta_backend.proposal.models import Proposal
from sipeta_backend.proposal.permissions import (
    IsMahasiswaCreateProposal,
    IsProposalUsers,
)
from sipeta_backend.proposal.serializers import ProposalSerializer
from sipeta_backend.semester.models import Semester
from sipeta_backend.users.permissions import IsNotEksternal
from sipeta_backend.utils.pagination import Pagination


class ProposalView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsMahasiswaCreateProposal)

    def post(self, request):
        form = ProposalCreationForm(request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(user=request.user)
            return Response({"id": proposal.id_proposal}, status=HTTP_201_CREATED)
        return Response(form.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request):
        active_semester = Semester._get_active_semester()
        proposals = Proposal.objects.filter(
            Q(semester=active_semester) | Q(status=PROPOSAL_STATUS_DITERIMA)
        )

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

        # proposal list pagination feature
        paginator = Pagination(
            proposals, request.GET.get("page"), request.GET.get("per_page")
        )
        proposals, paginator = paginator.get_content()
        print(proposals)

        serializer = ProposalSerializer(proposals, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class ProposalDetailView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsProposalUsers | IsNotEksternal,
    )

    @property
    def proposal(self):
        if not hasattr(self, "_proposal"):
            self._proposal = Proposal.objects.get(id_proposal=self.kwargs["id"])
        return self._proposal

    def get(self, request, *args, **kwargs):
        serializer = ProposalSerializer(self.proposal)
        return Response(serializer.data, status=HTTP_200_OK)
