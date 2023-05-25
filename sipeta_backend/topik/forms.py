from django import forms

from sipeta_backend.topik.models import Bidang


class BidangCreationForm(forms.ModelForm):
    class Meta:
        model = Bidang
        fields = ["name", "short"]
