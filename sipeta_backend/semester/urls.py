from django.urls import path

from sipeta_backend.semester.views import SemesterView

app_name = "semester"
urlpatterns = [
    path("", view=SemesterView.as_view()),
]
