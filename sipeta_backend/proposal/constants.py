# Proposal.status
PROPOSAL_STATUS_PENDING = "Pending"
PROPOSAL_STATUS_DITOLAK = "Ditolak"
PROPOSAL_STATUS_DISETUJUI = "Disetujui"
PROPOSAL_STATUS_DIBATALKAN = "Dibatalkan"

PROPOSAL_STATUS_CHOICES = (
    (PROPOSAL_STATUS_PENDING, PROPOSAL_STATUS_PENDING),
    (PROPOSAL_STATUS_DITOLAK, PROPOSAL_STATUS_DITOLAK),
    (PROPOSAL_STATUS_DISETUJUI, PROPOSAL_STATUS_DISETUJUI),
    (PROPOSAL_STATUS_DIBATALKAN, PROPOSAL_STATUS_DIBATALKAN),
)

# Proposal.sumber_ide
PROPOSAL_SUMBER_IDE_MAHASISWA = "Mahasiswa"
PROPOSAL_SUMBER_IDE_DOSEN = "Dosen"
PROPOSAL_SUMBER_IDE_MKM = "MKM"

PROPOSAL_SUMBER_IDE_CHOICES = (
    (PROPOSAL_SUMBER_IDE_MAHASISWA, PROPOSAL_SUMBER_IDE_MAHASISWA),
    (PROPOSAL_SUMBER_IDE_DOSEN, PROPOSAL_SUMBER_IDE_DOSEN),
    (PROPOSAL_SUMBER_IDE_MKM, PROPOSAL_SUMBER_IDE_MKM),
)

# InteraksiProposal.tipe
INTERAKSI_PROPOSAL_TIPE_KOMENTAR = "CMT"
INTERAKSI_PROPOSAL_TIPE_CHANGE_STATUS_PROPOSAL = "CSP"
INTERAKSI_PROPOSAL_TIPE_CHANGE_DOSEN_PEMBIMBING = "CDP"
INTERAKSI_PROPOSAL_TIPE_EDIT_JUDUL_PROPOSAL = "EJP"
INTERAKSI_PROPOSAL_TIPE_EDIT_BERKAS_PROPOSAL = "EBP"

INTERAKSI_PROPOSAL_TIPE_CHOICES = (
    (INTERAKSI_PROPOSAL_TIPE_KOMENTAR, "Komentar"),
    (INTERAKSI_PROPOSAL_TIPE_CHANGE_STATUS_PROPOSAL, "Change Status Proposal"),
    (INTERAKSI_PROPOSAL_TIPE_CHANGE_DOSEN_PEMBIMBING, "Change Dosen Pembimbing"),
    (INTERAKSI_PROPOSAL_TIPE_EDIT_JUDUL_PROPOSAL, "Edit Judul Proposal"),
    (INTERAKSI_PROPOSAL_TIPE_EDIT_BERKAS_PROPOSAL, "Edit Berkas Proposal"),
)
