from rest_framework import permissions


class IsProposalUsers(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user)
            and (
                (request.user in view.proposal.mahasiswas.all())
                or (request.user in view.proposal.dosen_pembimbings.all())
            )
        )
