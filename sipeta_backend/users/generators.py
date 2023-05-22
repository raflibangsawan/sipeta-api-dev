import random
import string

from django.contrib.auth import get_user_model

from sipeta_backend.users.constants import ROLE_DOSEN

User = get_user_model()


def generate_username(name, role):
    """
    Generate a unique username from the given name.
    """

    # ext.[username] is for dosen eksternal
    # sek.[username] is for staff sekre
    role_prefix = "ext." if role == ROLE_DOSEN else "sek."
    names = name.lower().split(" ")
    if len(names) == 1:
        username_temp = names[0]
    else:
        username_temp = names[0] + "." + names[-1]
    username_temp = role_prefix + username_temp
    counter = 1
    username = f"{username_temp}{str(counter).zfill(2)}"
    while User.objects.filter(username=username).exists():
        counter += 1
        username = f"{username_temp}{str(counter).zfill(2)}"
    return username


def generate_password():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))
