from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from sipeta_backend.proposal.forms import ProposalCreationForm
from sipeta_backend.proposal.models import Proposal
from sipeta_backend.proposal.permissions import (
    IsMahasiswaCreateProposal,
    IsProposalUsers,
)
from sipeta_backend.proposal.serializers import ProposalSerializer
from sipeta_backend.users.permissions import IsNotEksternal


class ProposalView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsMahasiswaCreateProposal)

    def post(self, request):
        form = ProposalCreationForm(request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(user=request.user)
            return Response({"id": proposal.id_proposal}, status=HTTP_201_CREATED)
        return Response(form.errors, status=HTTP_400_BAD_REQUEST)


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
