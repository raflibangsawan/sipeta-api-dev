from django.urls import path

from sipeta_backend.proposal.views import (
    ProposalChangeStatusPengajuanView,
    ProposalDetailView,
    ProposalView,
)

app_name = "proposal"
urlpatterns = [
    path("", view=ProposalView.as_view()),
    path("change_status", view=ProposalChangeStatusPengajuanView.as_view()),
    path("<uuid:id>/", view=ProposalDetailView.as_view()),
]
