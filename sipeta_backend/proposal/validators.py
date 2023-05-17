import os

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

from sipeta_backend.constants import VALID_TUPLE


def validate_file_size(file):
    max_file_size = 10485760  # 10 MB
    file_size = file.size

    if file_size > max_file_size:
        raise ValidationError(
            f"File tidak boleh melebihi {filesizeformat(max_file_size)}! \
            Ukuran file anda saat ini adalah {filesizeformat(file_size)}"
        )


def validate_file_extension(file):
    valid_extensions = [".pdf", ".ppt", ".pptx"]
    file_extension = os.path.splitext(file.name)[1]

    if file_extension not in valid_extensions:
        raise ValidationError(
            f"File tidak valid! \
            Ekstensi file harus berupa {', '.join(valid_extensions)}"
        )


def validate_mahasiswas_unique(mahasiswas):
    if len(mahasiswas) != len(set(mahasiswas)):
        return ("Terdapat mahasiswa yang duplikat!", False)
    return VALID_TUPLE


def validate_mahasiswas_count(mahasiswas):
    if len(mahasiswas) < 1:
        return ("Mahasiswa tidak boleh kosong!", False)
    if len(mahasiswas) > 3:
        return ("Mahasiswa tidak boleh lebih dari 3!", False)
    return VALID_TUPLE


def validate_dosen_pembimbings_unique(dosen_pembimbings):
    if len(dosen_pembimbings) != len(set(dosen_pembimbings)):
        return ("Terdapat dosen pembimbing yang duplikat!", False)
    return VALID_TUPLE


def validate_dosen_pembimbings_count(dosen_pembimbings):
    if len(dosen_pembimbings) > 2:
        return ("Dosen pembimbing tidak boleh lebih dari 2!", False)
    return VALID_TUPLE
