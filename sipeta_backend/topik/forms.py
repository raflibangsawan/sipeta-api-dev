import json

from django import forms

from sipeta_backend.topik.models import Bidang, Topik


class BidangCreationForm(forms.ModelForm):
    class Meta:
        model = Bidang
        fields = ["name", "short"]


class TopikCreationForm(forms.ModelForm):
    list_bidang = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Topik
        fields = ["title", "list_bidang", "pengerjaan", "content"]

    def save(self, commit=True, *args, **kwargs):
        topik = super().save(commit=False)
        if kwargs.get("created_by"):
            topik.created_by = kwargs.get("created_by")
        if commit:
            topik.save()
            topik.bidangs.set(self.cleaned_data["bidangs"])
        return topik

    def clean(self):
        cleaned_data = super().clean()
        try:
            list_bidang = json.loads(cleaned_data.get("list_bidang"))
        except json.JSONDecodeError:
            raise forms.ValidationError("Format list_bidang tidak valid")
        bidangs = []
        for id_bidang in list_bidang:
            try:
                bidangs.append(Bidang.objects.get(id=id_bidang))
            except Bidang.DoesNotExist:
                raise forms.ValidationError(
                    f"Bidang dengan id {id_bidang} tidak ditemukan"
                )
        cleaned_data["bidangs"] = bidangs
        return cleaned_data


class TopikUpdateForm(TopikCreationForm):
    class Meta(TopikCreationForm.Meta):
        fields = TopikCreationForm.Meta.fields + ["ketersediaan"]
