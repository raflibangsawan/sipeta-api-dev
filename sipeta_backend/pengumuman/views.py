from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

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
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        current_semester = Semester._get_active_semester()
        pengumumans = Pengumuman.objects.filter(semester=current_semester)
        serializer = PengumumanSerializer(pengumumans, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


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
