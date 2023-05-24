from django.core.exceptions import ValidationError


def validate_periode_semester(value):
    """
    Validate periode semester.
    Format: <tahun_awal>/<tahun_akhir>
    Contoh: 2020/2021
    """
    split_value = value.split("/")
    if len(split_value) != 2:
        raise ValidationError("Periode semester tidak valid.")

    a = split_value[0]
    b = split_value[1]
    if (
        not a.isdigit()
        or not b.isdigit()
        or len(a) != 4
        or len(b) != 4
        or int(a) != int(b) - 1
    ):
        raise ValidationError("Periode semester tidak valid.")
