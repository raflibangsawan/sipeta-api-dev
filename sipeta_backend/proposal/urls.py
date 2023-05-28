from django.urls import path

from sipeta_backend.proposal.views import (
    ProposalCancelView,
    ProposalChangeStatusPengajuanView,
    ProposalDetailView,
    ProposalDosenInterestView,
    ProposalDownloadListView,
    ProposalFormPopulateView,
    ProposalView,
)

app_name = "proposal"
urlpatterns = [
    path("", view=ProposalView.as_view()),
    path("change_status", view=ProposalChangeStatusPengajuanView.as_view()),
    path("<uuid:id>/", view=ProposalDetailView.as_view()),
    path("<uuid:id>/interest", view=ProposalDosenInterestView.as_view()),
    path("<uuid:id>/cancel", view=ProposalCancelView.as_view()),
    path("<uuid:id>/form", view=ProposalFormPopulateView.as_view()),
    path("download_proposal", view=ProposalDownloadListView.as_view()),
]
