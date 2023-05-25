from django.contrib.auth import get_user_model
from rest_framework import serializers

from sipeta_backend.proposal.constants import PROPOSAL_STATUS_DISETUJUI
from sipeta_backend.proposal.models import Proposal
from sipeta_backend.semester.models import Semester

User = get_user_model()


class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)


class UserSerializer(serializers.ModelSerializer):
    role_pengguna = serializers.CharField(source="role_as_integer")

    class Meta:
        model = User
        fields = ["id_user", "kode_identitas", "name", "role_pengguna"]


class DaftarDosenSerializer(serializers.ModelSerializer):
    jumlah_bimbingan = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["name", "jumlah_bimbingan"]

    def get_jumlah_bimbingan(self, obj):
        semester = Semester._get_active_semester()
        return (
            Proposal.objects.filter(
                semester=semester,
                status=PROPOSAL_STATUS_DISETUJUI,
                dosen_pembimbings__in=[obj],
            )
            .distinct()
            .count()
        )
