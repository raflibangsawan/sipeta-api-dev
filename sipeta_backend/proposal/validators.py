import os

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


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
