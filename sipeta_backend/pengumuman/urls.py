from django.urls import path

from sipeta_backend.pengumuman.views import PengumumanDetailView, PengumumanView

app_name = "pengumuman"
urlpatterns = [
    path("", view=PengumumanView.as_view()),
    path("<uuid:id>/", view=PengumumanDetailView.as_view()),
]
