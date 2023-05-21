# USERS ROLES
ROLE_MAHASISWA = "mahasiswa"
ROLE_DOSEN = "dosen"
ROLE_STAFF_SEKRE = "staff sekre"
ROLE_ADMIN = "admin"

# USERS PROGRAM STUDI
PRODI_S1_IK_REG = "S1 Ilkom Reguler"
PRODI_S1_IK_PAR = "S1 Ilkom Paralel"
PRODI_S1_IK_KI = "S1 Ilkom KI"
PRODI_S1_SI_REG = "S1 SI Reguler"
PRODI_S1_SI_PAR = "S1 SI Paralel"
PRODI_S1_SI_EKT = "S1 SI Ekstensi"
PRODI_CHOICES = (
    (PRODI_S1_IK_REG, PRODI_S1_IK_REG),
    (PRODI_S1_IK_PAR, PRODI_S1_IK_PAR),
    (PRODI_S1_IK_KI, PRODI_S1_IK_KI),
    (PRODI_S1_SI_REG, PRODI_S1_SI_REG),
    (PRODI_S1_SI_PAR, PRODI_S1_SI_PAR),
    (PRODI_S1_SI_EKT, PRODI_S1_SI_EKT),
)

# LDAP URLS
LDAP_FASILKOM_URL = "https://api.cs.ui.ac.id/authentication/ldap/v2/"
DOSEN_FASILKOM_URL = "https://apps.cs.ui.ac.id/webservice/detil_dosen.php?nip="
MAHASISWA_FASILKOM_URL = "https://apps.cs.ui.ac.id/webservice/detil_mahasiswa.php?npm="
