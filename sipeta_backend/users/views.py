import requests
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.views import APIView

from sipeta_backend.constants import EXCEL_FILE_MIME_TYPE
from sipeta_backend.users.authentication import expires_in, token_expire_handler
from sipeta_backend.users.constants import (
    DOSEN_FASILKOM_URL,
    LDAP_FASILKOM_URL,
    ROLE_DOSEN,
    ROLE_MAHASISWA,
)
from sipeta_backend.users.forms import UserStaffAndDosenEksternalCreationForm
from sipeta_backend.users.generators import generate_password
from sipeta_backend.users.models import create_akun_mahasiswa_from_npm
from sipeta_backend.users.permissions import (
    IsAdmin,
    IsDosenEksternal,
    IsNotEksternal,
    IsStaffSekre,
)
from sipeta_backend.users.serializers import UserSerializer, UserSigninSerializer
from sipeta_backend.utils.parser import (
    get_filename_and_mimetype,
    parse_xlsx_to_list_of_dict,
)

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
                    "role_pengguna": user.role_as_integer,
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
                "role_pengguna": user.role_as_integer,
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


class UserStaffAndDosenEksternalRegisterView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin | IsStaffSekre)

    def post(self, request):
        form = UserStaffAndDosenEksternalCreationForm(request.POST)
        if form.is_valid():
            password = generate_password()
            user = form.save(password=password)
            return Response(
                {"username": user.username, "password": password},
                status=HTTP_201_CREATED,
            )

        return Response(
            {"msg": "Gagal menambahkan user", "error": form.errors},
            status=HTTP_400_BAD_REQUEST,
        )


class UserMahasiswaRegisterView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin | IsStaffSekre)

    def post(self, request):
        kode_identitas = request.POST.get("kode_identitas")
        program_studi = request.POST.get("program_studi")

        if kode_identitas is None or program_studi is None:
            return Response(
                {
                    "msg": "Gagal menambahkan user",
                    "error": "kode_identitas dan program_studi tidak boleh kosong",
                },
                status=HTTP_400_BAD_REQUEST,
            )
        if not kode_identitas.isdigit():
            return Response(
                {
                    "msg": "Gagal menambahkan user",
                    "error": "kode_identitas harus berupa angka",
                },
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            User.objects.get(kode_identitas=kode_identitas)
            return Response(
                {
                    "msg": "Gagal menambahkan user",
                    "error": "kode_identitas sudah terdaftar",
                },
                status=HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            pass

        create_akun_mahasiswa_from_npm(npm=kode_identitas, program_studi=program_studi)
        return Response(
            {"msg": f"Mahasiswa dengan npm {kode_identitas} berhasil ditambahkan"},
            status=HTTP_201_CREATED,
        )


class BulkRegisterMahasiswaView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdmin | IsStaffSekre)

    def post(self, request):
        file = request.FILES.get("file")
        if file is None:
            return Response(
                {"msg": "Gagal menambahkan user", "error": "File tidak boleh kosong"},
                status=HTTP_400_BAD_REQUEST,
            )
        _, mime_type = get_filename_and_mimetype(file.name)
        if mime_type != EXCEL_FILE_MIME_TYPE:
            return Response(
                {
                    "msg": "Gagal menambahkan user",
                    "error": "File harus berformat excel",
                },
                status=HTTP_400_BAD_REQUEST,
            )

        datas = parse_xlsx_to_list_of_dict(file, ["npm", "program_studi"])
        created_account = 0
        errors = []
        for data in datas:
            try:
                create_akun_mahasiswa_from_npm(data["npm"], data["program_studi"])
                created_account += 1
            except Exception as e:
                errors.append(
                    "Gagal menambahkan user dengan npm {}: {}".format(
                        data["npm"], str(e)
                    )
                )

        if created_account > 0:
            return Response(
                {
                    "msg": f"Berhasil menambahkan {created_account} user",
                    "errors": errors,
                },
                status=HTTP_201_CREATED,
            )
        return Response(
            {"msg": "Gagal menambahkan user", "errors": errors},
            status=HTTP_400_BAD_REQUEST,
        )


class UserChangePasswordView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsDosenEksternal | IsAdmin | IsStaffSekre,
    )

    def patch(self, request):
        user = request.user
        password_old = request.POST.get("password_old")

        if not user.check_password(password_old):
            return Response({"msg": "Password lama salah"}, status=HTTP_400_BAD_REQUEST)

        password_new = request.POST.get("password_new")
        password_confirm = request.POST.get("password_confirm")

        if password_new is None or password_new == "":
            return Response(
                {"msg": "Password baru tidak boleh kosong"}, status=HTTP_400_BAD_REQUEST
            )

        if password_confirm is None or password_confirm == "":
            return Response(
                {"msg": "Konfirmasi password tidak boleh kosong"},
                status=HTTP_400_BAD_REQUEST,
            )

        if password_new == password_old:
            return Response(
                {"msg": "Password baru tidak boleh sama dengan password lama"},
                status=HTTP_400_BAD_REQUEST,
            )

        if password_new != password_confirm:
            return Response(
                {"msg": "Password baru tidak sama dengan konfirmasi password"},
                status=HTTP_400_BAD_REQUEST,
            )

        user.set_password(password_new)
        user.save()

        return Response({"msg": "Password berhasil diubah"}, status=HTTP_200_OK)


class AbstractUserView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsNotEksternal,
    )

    def get(self, request):
        src = request.GET.get("src", "")
        if not src.isdigit():
            src = ".*" + src.replace(" ", ".*") + ".*"
        else:
            src = "^" + src
        queryset = self.queryset
        queryset = queryset.filter(Q(kode_identitas__iregex=src) | Q(name__iregex=src))
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class MahasiswaView(AbstractUserView):
    queryset = User.objects.filter(role_pengguna=ROLE_MAHASISWA)


class DosenView(AbstractUserView):
    queryset = User.objects.filter(role_pengguna=ROLE_DOSEN)
