from django.urls import path

from sipeta_backend.users.views import (
    BulkRegisterMahasiswaView,
    DaftarDosenView,
    DosenFasilkomView,
    DosenTAView,
    DosenView,
    LoginView,
    LogoutView,
    MahasiswaView,
    UserChangePasswordView,
    UserMahasiswaRegisterView,
    UserStaffAndDosenEksternalRegisterView,
)

app_name = "users"
urlpatterns = [
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("register/", view=UserStaffAndDosenEksternalRegisterView.as_view()),
    path("register/mahasiswa/", view=UserMahasiswaRegisterView.as_view()),
    path("register/mahasiswa/bulk/", view=BulkRegisterMahasiswaView.as_view()),
    path("change_password", view=UserChangePasswordView.as_view()),
    path("dosen_ta", view=DosenTAView.as_view()),
    path("dosen_fasilkom", view=DosenFasilkomView.as_view()),
    path("mahasiswa", view=MahasiswaView.as_view(), name="mahasiswa"),
    path("dosen", view=DosenView.as_view(), name="dosen"),
    path("daftar_dosen", view=DaftarDosenView.as_view()),
]
