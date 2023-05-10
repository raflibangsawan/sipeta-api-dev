from django.urls import path

from sipeta_backend.users.views import LoginView, LogoutView

app_name = "users"
urlpatterns = [
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
]
