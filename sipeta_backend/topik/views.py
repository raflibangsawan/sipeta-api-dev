from datetime import datetime

from django.db.models import Q
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from sipeta_backend.topik.filters import TopikFilter
from sipeta_backend.topik.forms import (
    BidangCreationForm,
    TopikCreationForm,
    TopikUpdateForm,
)
from sipeta_backend.topik.models import Bidang, Topik
from sipeta_backend.topik.permissions import IsTopikUsers
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

        # topik list search feature
        src = request.GET.get("src", None)
        if src:
            src = ".*" + src.replace(" ", ".*") + ".*"
            topiks = topiks.filter(
                Q(title__iregex=src) | Q(created_by__name__iregex=src)
            ).distinct()

        # topik list filter feature
        topiks = TopikFilter.filter(topiks, **(request.GET.dict()))

        # topik list pagination feature
        paginator = Pagination(
            topiks, request.GET.get("page"), request.GET.get("per_page")
        )
        topiks, paginator = paginator.get_content()

        serializer = TopikSerializer(topiks, many=True)
        return Response(
            {
                "page_range": paginator.paginator.get_elided_page_range(
                    paginator.number, on_each_side=2, on_ends=1
                ),
                "topiks": serializer.data,
            },
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
    permission_classes = (
        IsMethodReadOnly
        | (permissions.IsAuthenticated & IsDosenFasilkom & IsTopikUsers),
    )

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

    def put(self, requests, *args, **kwargs):
        form = TopikUpdateForm(requests.POST, instance=self.topik)
        if form.is_valid():
            form.save()
            return Response({"msg": "Topik berhasil diubah"}, status=HTTP_200_OK)
        return Response(
            {"msg": "Topik gagal diubah", "errors": form.errors},
            status=HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        topik = self.topik
        topik.deleted_on = datetime.now()
        topik.save()
        return Response({"msg": "Topik berhasil dihapus"}, status=HTTP_200_OK)


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
