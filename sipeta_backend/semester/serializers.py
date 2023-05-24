from rest_framework import serializers

from sipeta_backend.semester.models import Semester


class SemesterSerializer(serializers.ModelSerializer):
    semester = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = ["id", "semester", "is_active"]

    def get_semester(self, obj):
        return obj.__str__()
