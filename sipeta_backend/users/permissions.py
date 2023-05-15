from rest_framework import permissions

from sipeta_backend.users.constants import (
    ROLE_ADMIN,
    ROLE_DOSEN,
    ROLE_MAHASISWA,
    ROLE_STAFF_SEKRE,
)


class IsNotEksternal(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool((request.user) and (not request.user.is_dosen_eksternal))


class IsMahasiswa(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool((request.user) and (request.user.role_pengguna == ROLE_MAHASISWA))


class IsDosen(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool((request.user) and (request.user.role_pengguna == ROLE_DOSEN))


class IsDosenFasilkom(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user)
            and (request.user.role_pengguna == ROLE_DOSEN)
            and (not request.user.is_dosen_eksternal)
        )


class IsDosenEksternal(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user)
            and (request.user.role_pengguna == ROLE_DOSEN)
            and (request.user.is_dosen_eksternal)
        )


class IsDosenTa(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user)
            and (request.user.role_pengguna == ROLE_DOSEN)
            and (request.user.is_dosen_ta)
        )


class IsStaffSekre(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool((request.user) and (request.user.role_pengguna == ROLE_STAFF_SEKRE))


class IsDosenTaOrStaffSekre(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user)
            and (
                (
                    (request.user.role_pengguna == ROLE_DOSEN)
                    and (request.user.is_dosen_ta)
                )
                or (request.user.role_pengguna == ROLE_STAFF_SEKRE)
            )
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user)
            and (request.user.is_superuser)
            and (request.user.role_pengguna == ROLE_ADMIN)
        )
