from rest_framework import serializers

from sipeta_backend.proposal.models import Proposal


class ProposalSerializer(serializers.ModelSerializer):
    berkas_proposal = serializers.SerializerMethodField()
    mahasiswas = serializers.SerializerMethodField()
    dosen_pembimbings = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "id_proposal",
            "title",
            "sumber_ide",
            "berkas_proposal",
            "nama_berkas_proposal",
            "status",
            "created_on",
            "mahasiswas",
            "dosen_pembimbings",
        ]

    def get_berkas_proposal(self, obj):
        return obj.berkas_proposal.url

    def get_mahasiswas(self, obj):
        return [
            {
                "id": mahasiswa.id_user,
                "kode_identitas": mahasiswa.kode_identitas,
                "name": mahasiswa.name,
            }
            for mahasiswa in obj.mahasiswas.all()
        ]

    def get_dosen_pembimbings(self, obj):
        return [
            {
                "id": dosen_pembimbing.id_user,
                "kode_identitas": dosen_pembimbing.kode_identitas,
                "name": dosen_pembimbing.name,
            }
            for dosen_pembimbing in obj.dosen_pembimbings.all()
        ]
