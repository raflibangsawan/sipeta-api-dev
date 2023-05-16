from rest_framework import permissions

from sipeta_backend.users.constants import ROLE_MAHASISWA


class IsMahasiswaCreateProposal(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method != "POST" or request.user.role_pengguna == ROLE_MAHASISWA
        )


class IsProposalUsers(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user)
            and (
                (request.user in view.proposal.mahasiswas.all())
                or (request.user in view.proposal.dosen_pembimbings.all())
            )
        )
