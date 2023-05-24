from django.urls import path

from sipeta_backend.users.views import DosenView, LoginView, LogoutView, MahasiswaView

app_name = "users"
urlpatterns = [
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("mahasiswa", view=MahasiswaView.as_view(), name="mahasiswa"),
    path("dosen", view=DosenView.as_view(), name="dosen"),
]
