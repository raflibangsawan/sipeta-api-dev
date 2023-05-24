from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from sipeta_backend.pengumuman.models import Pengumuman
from sipeta_backend.pengumuman.serializers import PengumumanSerializer
from sipeta_backend.semester.models import Semester


class PengumumanView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        current_semester = Semester._get_active_semester()
        pengumumans = Pengumuman.objects.filter(semester=current_semester)
        serializer = PengumumanSerializer(pengumumans, many=True)
        return Response(serializer.data, status=200)
