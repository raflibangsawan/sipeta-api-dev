from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from sipeta_backend.semester.forms import SemesterForm
from sipeta_backend.semester.models import Semester
from sipeta_backend.semester.serializers import SemesterSerializer
from sipeta_backend.users.permissions import IsAdmin, IsMethodReadOnly, IsStaffSekre


class SemesterView(APIView):
    permission_classes = (
        (IsMethodReadOnly | (permissions.IsAuthenticated & (IsAdmin | IsStaffSekre))),
    )

    def get(self, request, *args, **kwargs):
        if request.GET.get("active"):
            semester = Semester._get_active_semester()
            serializer = SemesterSerializer(semester)
            return Response(serializer.data, status=HTTP_200_OK)

        semesters = Semester.objects.all()
        serializer = SemesterSerializer(semesters, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        id = request.POST.get("id")
        if id:
            try:
                semester = Semester.objects.get(id=id)
                Semester._set_active_semester(semester)
                return Response(
                    {"msg": "Berhasil mengubah semester aktif."}, status=HTTP_200_OK
                )
            except Semester.DoesNotExist:
                pass

        semester = request.POST.get("semester")
        periode = request.POST.get("periode")

        try:
            semester = Semester.objects.get(semester=semester, periode=periode)
            if semester.is_active:
                return Response(
                    {
                        "msg": "Gagal mengubah semester aktif.",
                        "errors": "Semester sudah aktif.",
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

            Semester._set_active_semester(semester)
            return Response(
                {"msg": "Berhasil mengubah semester aktif."}, status=HTTP_200_OK
            )
        except Semester.DoesNotExist:
            form = SemesterForm(request.POST)
            if form.is_valid():
                semester = form.save()
                Semester._set_active_semester(semester)
                return Response(
                    {"msg": "Berhasil mengubah semester aktif."},
                    status=HTTP_201_CREATED,
                )

        return Response(
            {"msg": "Gagal mengubah semester aktif.", "errors": form.errors},
            status=HTTP_400_BAD_REQUEST,
        )
