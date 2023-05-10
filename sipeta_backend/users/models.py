import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, CharField, UUIDField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for SIPETA Backend.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    id_user = UUIDField(_("ID"), default=uuid.uuid4, editable=False)

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Nama Lengkap"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    kode_identitas = CharField(_("Kode Identitas"), blank=True, max_length=255)
    role_pengguna = CharField(_("Role Pengguna"), blank=True, max_length=255)
    is_dosen_eksternal = BooleanField(_("Dosen Eksternal"), blank=False, default=False)
