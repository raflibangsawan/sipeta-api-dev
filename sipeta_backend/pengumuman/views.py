from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from sipeta_backend.pengumuman.forms import PengumumanCreationForm
from sipeta_backend.pengumuman.models import Pengumuman
from sipeta_backend.pengumuman.serializers import PengumumanSerializer
from sipeta_backend.semester.models import Semester
from sipeta_backend.users.permissions import (
    IsAdmin,
    IsDosenTa,
    IsMethodReadOnly,
    IsStaffSekre,
)


class PengumumanView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAdmin | IsStaffSekre | IsDosenTa | IsMethodReadOnly,
    )

    def get(self, request):
        current_semester = Semester._get_active_semester()
        pengumumans = Pengumuman.objects.filter(semester=current_semester)
        serializer = PengumumanSerializer(pengumumans, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        form = PengumumanCreationForm(request.POST, request.FILES)
        if form.is_valid():
            pengumuman = form.save(user=request.user)
            return Response({"id": pengumuman.id_pengumuman}, status=HTTP_201_CREATED)
        return Response(form.errors, status=HTTP_400_BAD_REQUEST)


class PengumumanDetailView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAdmin | IsStaffSekre | IsDosenTa | IsMethodReadOnly,
    )

    @property
    def pengumuman(self):
        if not hasattr(self, "_pengumuman"):
            self._pengumuman = Pengumuman.objects.get(id_pengumuman=self.kwargs["id"])
        return self._pengumuman

    def get(self, request, *args, **kwargs):
        serializer = PengumumanSerializer(self.pengumuman)
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        self.pengumuman.delete()
        return Response({"msg": "Pengumuman berhasil dihapus"}, status=HTTP_200_OK)
