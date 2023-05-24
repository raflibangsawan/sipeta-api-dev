from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from sipeta_backend.users.constants import ROLE_DOSEN, ROLE_STAFF_SEKRE
from sipeta_backend.users.generators import generate_username

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

        error_messages = {
            "username": {"unique": _("This username has already been taken.")}
        }


class UserStaffAndDosenEksternalCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "role_pengguna"]

    def save(self, commit=True, *args, **kwargs):
        user = User(**self.cleaned_data)
        user.set_password(kwargs.get("password"))
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get("name")
        role_pengguna = cleaned_data.get("role_pengguna")

        if role_pengguna == ROLE_DOSEN:
            cleaned_data["is_dosen_eksternal"] = True

        cleaned_data["username"] = generate_username(name, role_pengguna)

        return cleaned_data

    def clean_role_pengguna(self):
        role_pengguna = self.cleaned_data.get("role_pengguna")
        if role_pengguna != ROLE_DOSEN and role_pengguna != ROLE_STAFF_SEKRE:
            raise forms.ValidationError(
                "Cannot create user with role other than Dosen or Staff Sekre"
            )
        return role_pengguna
