from django.urls import path

from sipeta_backend.topik.views import BidangView, TopikDetailView, TopikView

app_name = "topik"
urlpatterns = [
    path("", view=TopikView.as_view()),
    path("<uuid:id>/", view=TopikDetailView.as_view()),
    path("bidang", view=BidangView.as_view()),
]
