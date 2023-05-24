from django import forms

from sipeta_backend.pengumuman.models import Pengumuman
from sipeta_backend.semester.models import Semester


class PengumumanCreationForm(forms.ModelForm):
    class Meta:
        model = Pengumuman
        fields = ["title", "content", "lampiran"]

    def save(self, commit=True, *args, **kwargs):
        pengumuman = super().save(commit=False)
        pengumuman.semester = Semester._get_active_semester()
        if self.cleaned_data["lampiran"]:
            pengumuman.nama_lampiran = self.cleaned_data["lampiran"].name
        pengumuman.created_by = kwargs.get("user")
        if commit:
            pengumuman.save()
        return pengumuman
