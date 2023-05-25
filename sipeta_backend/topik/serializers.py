from rest_framework import serializers

from sipeta_backend.topik.models import Bidang, Topik


class BidangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bidang
        fields = ["id", "name", "short"]


class TopikSerializer(serializers.ModelSerializer):
    bidangs = serializers.SerializerMethodField()
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Topik
        fields = [
            "id_topik",
            "title",
            "ketersediaan",
            "bidangs",
            "pengerjaan",
            "content",
            "created_by",
            "created_on",
        ]

    def get_bidangs(self, obj):
        return BidangSerializer(obj.bidangs.all(), many=True).data


class TopikDetailSerializer(TopikSerializer):
    kontak = serializers.SerializerMethodField()

    class Meta(TopikSerializer.Meta):
        fields = TopikSerializer.Meta.fields + ["kontak"]

    def get_kontak(self, obj):
        return obj.created_by.email
