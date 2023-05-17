from rest_framework import serializers

from sipeta_backend.proposal.models import InteraksiProposal, Proposal
from sipeta_backend.users.serializers import UserSerializer


class ProposalListSerializer(serializers.ModelSerializer):
    semester = serializers.StringRelatedField()
    mahasiswas = serializers.SerializerMethodField()
    dosen_pembimbings = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "id_proposal",
            "semester",
            "title",
            "status",
            "mahasiswas",
            "dosen_pembimbings",
        ]

    def get_mahasiswas(self, obj):
        return UserSerializer(obj.mahasiswas.all(), many=True).data

    def get_dosen_pembimbings(self, obj):
        return UserSerializer(obj.dosen_pembimbings.all(), many=True).data


class ProposalSerializer(serializers.ModelSerializer):
    semester = serializers.StringRelatedField()
    berkas_proposal = serializers.SerializerMethodField()
    mahasiswas = serializers.SerializerMethodField()
    dosen_pembimbings = serializers.SerializerMethodField()
    interaksi_proposals = serializers.SerializerMethodField()
    dosen_tertariks = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "id_proposal",
            "semester",
            "title",
            "sumber_ide",
            "berkas_proposal",
            "nama_berkas_proposal",
            "status",
            "created_on",
            "mahasiswas",
            "dosen_pembimbings",
            "dosen_tertariks",
            "interaksi_proposals",
        ]

    def get_berkas_proposal(self, obj):
        return obj.berkas_proposal.url

    def get_mahasiswas(self, obj):
        return UserSerializer(obj.mahasiswas.all(), many=True).data

    def get_dosen_pembimbings(self, obj):
        return UserSerializer(obj.dosen_pembimbings.all(), many=True).data

    def get_interaksi_proposals(self, obj):
        return InteraksiProposalSerializer(
            obj.interaksi_proposals.all(), many=True
        ).data

    def get_dosen_tertariks(self, obj):
        return UserSerializer(obj.dosen_tertariks.all(), many=True).data


class InteraksiProposalSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    class Meta:
        model = InteraksiProposal
        fields = [
            "tipe",
            "content",
            "created_by",
            "created_on",
        ]
