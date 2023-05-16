from django.urls import path

from sipeta_backend.proposal.views import ProposalDetailView, ProposalView

app_name = "proposal"
urlpatterns = [
    path("", view=ProposalView.as_view()),
    path("<uuid:id>/", view=ProposalDetailView.as_view()),
]
