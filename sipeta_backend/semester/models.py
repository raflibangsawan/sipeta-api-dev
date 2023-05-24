import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from sipeta_backend.semester.constants import (
    SEMESTER_CHOICES,
    SEMESTER_GASAL,
    SEMESTER_GENAP,
)


def calculate_current_semester():
    from datetime import datetime

    now = datetime.now()
    current_month = now.month
    current_year = now.year
    if current_month >= 2 and current_month <= 7:
        return SEMESTER_GENAP, f"{current_year-1}/{current_year}"
    else:
        return SEMESTER_GASAL, f"{current_year}/{current_year+1}"


class Semester(models.Model):
    id_semester = models.UUIDField(_("ID"), default=uuid.uuid4, editable=False)
    semester = models.CharField(
        max_length=10,
        null=False,
        default=calculate_current_semester()[0],
        choices=SEMESTER_CHOICES,
    )
    periode = models.CharField(
        max_length=9, null=False, default=calculate_current_semester()[1]
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("semester", "periode")
        ordering = ["-periode", "-semester"]

    def __str__(self) -> str:
        return f"{self.semester} {self.periode}"

    @staticmethod
    def _get_active_semester():
        active_semester = Semester.objects.filter(is_active=True).first()
        return active_semester if active_semester else Semester.objects.first()
