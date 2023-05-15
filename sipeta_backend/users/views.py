import requests
from django.contrib.auth import authenticate, get_user_model
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.views import APIView

from sipeta_backend.users.authentication import expires_in, token_expire_handler
from sipeta_backend.users.constants import (
    DOSEN_FASILKOM_URL,
    LDAP_FASILKOM_URL,
    ROLE_ADMIN,
    ROLE_DOSEN,
    ROLE_MAHASISWA,
    ROLE_STAFF_SEKRE,
)
from sipeta_backend.users.serializers import UserSigninSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        signin_serializer = UserSigninSerializer(data=request.data)

        if not signin_serializer.is_valid():
            return Response(signin_serializer.errors, status=HTTP_400_BAD_REQUEST)

        login_credentials = {
            "username": signin_serializer.data["username"],
            "password": signin_serializer.data["password"],
        }

        try:
            ldap_result = requests.post(
                LDAP_FASILKOM_URL, json=login_credentials
            ).json()
        except requests.exceptions.RequestException:
            ldap_result = {"state": None, "nama_role": "Gagal Login"}

        if ldap_result["state"] == 0:
            # Handle Login buat admin dan dosen eksternal (akun yang tidak terdaftar di SSO UI)
            user = authenticate(
                username=login_credentials["username"],
                password=login_credentials["password"],
            )
            if not user:
                return Response(
                    {"msg": "Autentikasi gagal: username atau password salah"},
                    status=HTTP_401_UNAUTHORIZED,
                )

            # TOKEN STUFF
            token, _ = Token.objects.get_or_create(user=user)

            # token_expire_handler will check, if the token is expired it will generate new one
            _, token = token_expire_handler(token)

            return Response(
                {
                    "id": user.id_user,
                    "name": user.name,
                    "role_pengguna": map_user_role_to_integer(
                        user.role_pengguna, user.is_dosen_ta
                    ),
                    "expires_in": expires_in(token),
                    "token": token.key,
                },
                status=HTTP_200_OK,
            )

        id = "None"
        # Handle login mahasiswa dan dosen yang berhasil login lewat ldap
        if ldap_result["nama_role"] == ROLE_MAHASISWA:
            # 1. Cek ke tabel mahasiswa ada atau engga
            # 2. Kalau enggak ada, akun mahasiswa belum terdaftar di sistem maka return error
            try:
                mahasiswa_user = User.objects.get(
                    username=login_credentials["username"], role_pengguna=ROLE_MAHASISWA
                )
            except User.DoesNotExist:
                return Response(
                    {"msg": "Autentikasi gagal: mahasiswa belum terdaftar pada sistem"},
                    status=HTTP_401_UNAUTHORIZED,
                )
            id = mahasiswa_user.id_user
        elif ldap_result["state"] == 1:
            # 1. Cek ke tabel dosen ada atau engga
            try:
                dosen_user = User.objects.get(
                    username=login_credentials["username"], role_pengguna=ROLE_DOSEN
                )
            except User.DoesNotExist:
                # 2. Kalau enggak ada, maka bikin akun baru, get data dari LDAP
                nip_dosen = ldap_result["kodeidentitas"]
                data_dosen_from_ldap = requests.get(
                    DOSEN_FASILKOM_URL + nip_dosen
                ).json()
                dosen_user = User().objects.create_user(
                    username=login_credentials["username"],
                    password=login_credentials["password"],
                    name=data_dosen_from_ldap["nama"],
                    email=data_dosen_from_ldap["email"],
                    kode_identitas=data_dosen_from_ldap["nip"],
                    role_pengguna=ROLE_DOSEN,
                )
            id = dosen_user.id_user
        elif ldap_result["nama_role"] == "Gagal Login":
            # jika auth LDAP lagi gabisa diakses, tapi akun udah terdaftar di sistem
            try:
                user = User.objects.get(username=login_credentials["username"])
                id = user.id_user
            except User.DoesNotExist:
                return Response(
                    {
                        "msg": "Autentikasi gagal: LDAP gagal dan username tidak terdaftar pada sistem"
                    },
                    status=HTTP_401_UNAUTHORIZED,
                )

        user = authenticate(
            username=login_credentials["username"],
            password=login_credentials["password"],
        )

        # jika berhasil auth LDAP, tapi password di sistem berbeda dengan password di LDAP
        if not user and ldap_result["nama_role"] != "Gagal Login":
            user_reset_password = User.objects.get(
                username=login_credentials["username"]
            )
            user_reset_password.set_password(login_credentials["password"])
            user_reset_password.save()
            user = authenticate(
                username=login_credentials["username"],
                password=login_credentials["password"],
            )

        # TOKEN STUFF
        token, _ = Token.objects.get_or_create(user=user)

        # token_expire_handler will check, if the token is expired it will generate new one
        _, token = token_expire_handler(token)

        return Response(
            {
                "id": id,
                "name": user.name,
                "role_pengguna": map_user_role_to_integer(
                    user.role_pengguna, user.is_dosen_ta
                ),
                "expires_in": expires_in(token),
                "token": token.key,
            },
            status=HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        request.user.auth_token.delete()
        return Response(
            {"msg": "Logout berhasil: Token terhapus dari sistem"}, status=HTTP_200_OK
        )


def map_user_role_to_integer(user_role, is_dosen_ta):
    if user_role == ROLE_MAHASISWA:
        return "4564"
    elif user_role == ROLE_DOSEN:
        if is_dosen_ta:
            return "8714"
        return "8465"
    elif user_role == ROLE_STAFF_SEKRE:
        return "9344"
    elif user_role == ROLE_ADMIN:
        return "9812"
    else:
        return "0000"
