from django.db.models import Q
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from sipeta_backend.topik.forms import BidangCreationForm, TopikCreationForm
from sipeta_backend.topik.models import Bidang, Topik
from sipeta_backend.topik.serializers import (
    BidangSerializer,
    TopikDetailSerializer,
    TopikSerializer,
)
from sipeta_backend.users.permissions import IsDosenFasilkom, IsMethodReadOnly
from sipeta_backend.utils.pagination import Pagination


class TopikView(APIView):
    permission_classes = (
        IsMethodReadOnly | (permissions.IsAuthenticated & IsDosenFasilkom),
    )

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

    def post(self, request):
        form = TopikCreationForm(request.POST)
        if form.is_valid():
            topik = form.save(created_by=request.user)
            return Response(
                {"msg": "Topik berhasil ditambahkan", "id": topik.id_topik},
                status=HTTP_201_CREATED,
            )
        return Response(
            {"msg": "Topik gagal ditambahkan", "errors": form.errors},
            status=HTTP_400_BAD_REQUEST,
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


class BidangView(APIView):
    queryset = Bidang.objects.all()
    permission_classes = (
        IsMethodReadOnly | (permissions.IsAuthenticated & IsDosenFasilkom),
    )

    def get(self, request):
        src = request.GET.get("src", "")
        src = ".*" + src.replace(" ", ".*") + ".*"
        queryset = self.queryset
        queryset = queryset.filter(
            Q(name__iregex=src) | Q(short__iregex=src)
        ).distinct()
        serializer = BidangSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        form = BidangCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return Response(
                {"msg": "Bidang berhasil ditambahkan"}, status=HTTP_201_CREATED
            )
        return Response(
            {"msg": "Bidang gagal ditambahkan", "errors": form.errors},
            status=HTTP_400_BAD_REQUEST,
        )
