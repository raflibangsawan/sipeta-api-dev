from django.urls import path

from sipeta_backend.topik.views import TopikDetailView, TopikView

app_name = "topik"
urlpatterns = [
    path("", view=TopikView.as_view()),
    path("<uuid:id>/", view=TopikDetailView.as_view()),
]
