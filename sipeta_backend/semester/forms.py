from django import forms

from sipeta_backend.semester.models import Semester


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ["semester", "periode"]

    def save(self, commit=True):
        semester = super().save(commit=False)
        if commit:
            semester.save()
        return semester
