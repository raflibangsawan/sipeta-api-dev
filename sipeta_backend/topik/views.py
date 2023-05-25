from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from sipeta_backend.topik.models import Topik
from sipeta_backend.topik.serializers import TopikDetailSerializer, TopikSerializer
from sipeta_backend.utils.pagination import Pagination


class TopikView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        topiks = Topik.objects.filter(deleted_on__isnull=True)

        # topik list pagination feature
        paginator = Pagination(
            topiks, request.GET.get("page"), request.GET.get("per_page")
        )
        topiks, paginator = paginator.get_content()

        serializer = TopikSerializer(topiks, many=True)
        return Response(
            {"num_pages": paginator.paginator.num_pages, "topiks": serializer.data},
            status=HTTP_200_OK,
        )


class TopikDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    @property
    def topik(self):
        if not hasattr(self, "_topik"):
            self._topik = Topik.objects.get(id_topik=self.kwargs["id"])
        return self._topik

    def get(self, request, *args, **kwargs):
        # everyone can see topik and its detail
        # but only authenticated, non external user can see dosen's contact
        if request.user.is_authenticated and not request.user.is_dosen_eksternal:
            serializer = TopikDetailSerializer(self.topik)
        else:
            serializer = TopikSerializer(self.topik)
        return Response(serializer.data, status=HTTP_200_OK)
