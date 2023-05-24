from django.db.models import Count

from sipeta_backend.proposal.models import Proposal
from sipeta_backend.semester.models import Semester
from sipeta_backend.utils.string import to_bool


class ProposalFilter:
    def __filter_by_status(proposals, **kwargs):
        if kwargs.get("status") is None:
            return proposals
        return proposals.filter(status=kwargs["status"])

    def __filter_by_mahasiswa(proposals, **kwargs):
        if kwargs.get("mahasiswa") is None:
            return proposals
        return proposals.annotate(mahasiswa_count=Count("mahasiswas")).filter(
            mahasiswa_count=int(kwargs["mahasiswa"])
        )

    def __filter_by_dosen_pembimbing(proposals, **kwargs):
        if kwargs.get("dosen_pembimbing") is None:
            return proposals
        if to_bool(kwargs["dosen_pembimbing"]):
            return proposals.annotate(dosbing_count=Count("dosen_pembimbings")).filter(
                dosbing_count__gte=1
            )
        return proposals.annotate(dosbing_count=Count("dosen_pembimbings")).filter(
            dosbing_count=0
        )

    def __filter_by_semester(proposals, **kwargs):
        current_semester = Semester._get_active_semester()
        if kwargs.get("semester") is not None and to_bool(kwargs.get("semester")):
            return proposals.filter(semester=current_semester)
        return proposals

    def filter(proposals=None, **kwargs):
        """!
        Helper for filtering Proposal easily with mutiple parameter.

        @param proposals            QuerySet<Proposal> objects.

        Optional parameter:
        @param status               (String) proposal status case sensitive.
        @param mahasiswa            (Integer) mahasiswa count.
        @param dosen_pembimbing     (Boolean) has dosen_pembimbing or not.
        @param semester             (Boolean) if True filter current semester only.

        @return QuerySet<Proposal> contains result of filtered proposals.
        """
        if proposals is None:
            proposals = Proposal.objects.all()

        proposals = ProposalFilter.__filter_by_status(proposals, **kwargs)
        proposals = ProposalFilter.__filter_by_mahasiswa(proposals, **kwargs)
        proposals = ProposalFilter.__filter_by_dosen_pembimbing(proposals, **kwargs)
        proposals = ProposalFilter.__filter_by_semester(proposals, **kwargs)
        return proposals
