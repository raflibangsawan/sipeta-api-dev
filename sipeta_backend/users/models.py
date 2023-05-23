import uuid

import requests
from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, CharField, UUIDField
from django.utils.translation import gettext_lazy as _

from sipeta_backend.users.constants import (
    MAHASISWA_FASILKOM_URL,
    PRODI_CHOICES,
    ROLE_ADMIN,
    ROLE_DOSEN,
    ROLE_MAHASISWA,
    ROLE_STAFF_SEKRE,
)


class User(AbstractUser):
    """
    Default custom user model for SIPETA Backend.
    """

    id_user = UUIDField(_("ID"), default=uuid.uuid4, editable=False)

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Nama Lengkap"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    kode_identitas = CharField(_("Kode Identitas"), blank=True, max_length=255)
    program_studi = CharField(
        _("Program Studi"), blank=True, max_length=60, choices=PRODI_CHOICES
    )
    role_pengguna = CharField(_("Role Pengguna"), blank=True, max_length=255)
    is_dosen_ta = BooleanField(_("Dosen TA"), blank=False, default=False)
    is_dosen_eksternal = BooleanField(_("Dosen Eksternal"), blank=False, default=False)

    def __str__(self) -> str:
        return self.name

    @property
    def role_as_integer(self):
        if self.role_pengguna == ROLE_MAHASISWA:
            return "4564"
        elif self.role_pengguna == ROLE_DOSEN:
            if self.is_dosen_ta:
                return "8714"
            return "8465"
        elif self.role_pengguna == ROLE_STAFF_SEKRE:
            return "9344"
        elif self.role_pengguna == ROLE_ADMIN:
            return "9812"
        else:
            return "0000"


def create_akun_mahasiswa_from_npm(npm, program_studi):
    """
    Create a new user with the given NPM and program studi.
    Get data from LDAP.
    """
    data_from_ldap = requests.get(MAHASISWA_FASILKOM_URL + npm).json()
    user = User.objects.create_user(
        username=data_from_ldap["username"],
        name=data_from_ldap["nama"],
        email=data_from_ldap["email"],
        kode_identitas=npm,
        role_pengguna=ROLE_MAHASISWA,
        program_studi=program_studi,
    )
    user.set_unusable_password()
    user.save()
    return user
