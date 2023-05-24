from django.urls import path

from sipeta_backend.pengumuman.views import PengumumanView

app_name = "pengumuman"
urlpatterns = [
    path("", view=PengumumanView.as_view()),
]
