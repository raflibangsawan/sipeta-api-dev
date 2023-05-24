from django.conf import settings
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
        return [
            {"name": mahasiswa.name, "program_studi": mahasiswa.program_studi}
            for mahasiswa in obj.mahasiswas.all()
        ]

    def get_dosen_pembimbings(self, obj):
        return [
            {"name": dosen_pembimbing.name}
            for dosen_pembimbing in obj.dosen_pembimbings.all()
        ]


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
        return [
            {
                "name": mahasiswa.name,
                "kode_identitas": mahasiswa.kode_identitas,
                "program_studi": mahasiswa.program_studi,
            }
            for mahasiswa in obj.mahasiswas.all()
        ]

    def get_dosen_pembimbings(self, obj):
        return [
            {"name": dosen_pembimbing.name}
            for dosen_pembimbing in obj.dosen_pembimbings.all()
        ]

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


class ProposalDownloadListSerializer(serializers.ModelSerializer):
    judul_proposal = serializers.CharField(source="title")
    nama_mahasiswa_1 = serializers.SerializerMethodField()
    npm_mahasiswa_1 = serializers.SerializerMethodField()
    prodi_mahasiswa_1 = serializers.SerializerMethodField()
    nama_mahasiswa_2 = serializers.SerializerMethodField()
    npm_mahasiswa_2 = serializers.SerializerMethodField()
    prodi_mahasiswa_2 = serializers.SerializerMethodField()
    nama_mahasiswa_3 = serializers.SerializerMethodField()
    npm_mahasiswa_3 = serializers.SerializerMethodField()
    prodi_mahasiswa_3 = serializers.SerializerMethodField()
    nama_dosen_pembimbing_1 = serializers.SerializerMethodField()
    nama_dosen_pembimbing_2 = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "judul_proposal",
            "nama_mahasiswa_1",
            "npm_mahasiswa_1",
            "prodi_mahasiswa_1",
            "nama_mahasiswa_2",
            "npm_mahasiswa_2",
            "prodi_mahasiswa_2",
            "nama_mahasiswa_3",
            "npm_mahasiswa_3",
            "prodi_mahasiswa_3",
            "nama_dosen_pembimbing_1",
            "nama_dosen_pembimbing_2",
            "url",
        ]

    def get_nama_mahasiswa_1(self, obj):
        return obj.mahasiswas.all()[0].name

    def get_npm_mahasiswa_1(self, obj):
        return obj.mahasiswas.all()[0].kode_identitas

    def get_prodi_mahasiswa_1(self, obj):
        return obj.mahasiswas.all()[0].program_studi

    def get_nama_mahasiswa_2(self, obj):
        if obj.mahasiswas.all().count() < 2:
            return "-"
        return obj.mahasiswas.all()[1].name

    def get_npm_mahasiswa_2(self, obj):
        if obj.mahasiswas.all().count() < 2:
            return "-"
        return obj.mahasiswas.all()[1].kode_identitas

    def get_prodi_mahasiswa_2(self, obj):
        if obj.mahasiswas.all().count() < 2:
            return "-"
        return obj.mahasiswas.all()[1].program_studi

    def get_nama_mahasiswa_3(self, obj):
        if obj.mahasiswas.all().count() < 3:
            return "-"
        return obj.mahasiswas.all()[2].name

    def get_npm_mahasiswa_3(self, obj):
        if obj.mahasiswas.all().count() < 3:
            return "-"
        return obj.mahasiswas.all()[2].kode_identitas

    def get_prodi_mahasiswa_3(self, obj):
        if obj.mahasiswas.all().count() < 3:
            return "-"
        return obj.mahasiswas.all()[2].program_studi

    def get_nama_dosen_pembimbing_1(self, obj):
        if obj.dosen_pembimbings.all().count() < 1:
            return "-"
        return obj.dosen_pembimbings.all()[0].name

    def get_nama_dosen_pembimbing_2(self, obj):
        if obj.dosen_pembimbings.all().count() < 2:
            return "-"
        return obj.dosen_pembimbings.all()[1].name

    def get_url(self, obj):
        path = "/proposal/" + str(obj.id_proposal) + "/"
        if settings.DEBUG:
            return "http://localhost:8000" + path
        return settings.HOST_URL + path
