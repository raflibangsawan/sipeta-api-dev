from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)


class UserSerializer(serializers.ModelSerializer):
    role_pengguna = serializers.CharField(source="role_as_integer")

    class Meta:
        model = User
        fields = ["id_user", "kode_identitas", "name", "role_pengguna"]
