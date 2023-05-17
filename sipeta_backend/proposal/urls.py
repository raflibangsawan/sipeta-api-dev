from django.urls import path

from sipeta_backend.proposal.views import (
    ProposalChangeDosenPembimbingView,
    ProposalChangeStatusPengajuanView,
    ProposalChangeStatusView,
    ProposalDetailView,
    ProposalDosenInterestView,
    ProposalEditView,
    ProposalView,
)

app_name = "proposal"
urlpatterns = [
    path("", view=ProposalView.as_view()),
    path("change_status", view=ProposalChangeStatusPengajuanView.as_view()),
    path("<uuid:id>/", view=ProposalDetailView.as_view()),
    path("<uuid:id>/change_status", view=ProposalChangeStatusView.as_view()),
    path(
        "<uuid:id>/change_dosen_pembimbing",
        view=ProposalChangeDosenPembimbingView.as_view(),
    ),
    path("<uuid:id>/edit", view=ProposalEditView.as_view()),
    path("<uuid:id>/interest", view=ProposalDosenInterestView.as_view()),
]
