from rest_framework import serializers

from sipeta_backend.pengumuman.models import Pengumuman


class PengumumanSerializer(serializers.ModelSerializer):
    lampiran = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Pengumuman
        fields = [
            "id_pengumuman",
            "title",
            "content",
            "lampiran",
            "nama_lampiran",
            "created_by",
            "created_on",
        ]

    def get_lampiran(self, obj):
        return obj.lampiran.url if obj.lampiran else "-"
