from sipeta_backend.topik.models import Bidang, Topik


class TopikFilter:
    def __filter_by_bidang(topiks, **kwargs):
        if kwargs.get("bidang") is None:
            return topiks
        short = kwargs.get("bidang")
        try:
            bidang = Bidang.objects.get(short=short)
        except Bidang.DoesNotExist:
            return None
        return topiks.filter(bidangs__in=[bidang]).distinct()

    def __filter_by_ketersediaan(topiks, **kwargs):
        if kwargs.get("ketersediaan") is None:
            return topiks
        return topiks.filter(ketersediaan=kwargs.get("ketersediaan"))

    def __filter_by_pengerjaan(topiks, **kwargs):
        if kwargs.get("pengerjaan") is None:
            return topiks
        return topiks.filter(pengerjaan=int(kwargs.get("pengerjaan")))

    def filter(topiks=None, **kwargs):
        """!
        Helper for filtering topik easily with mutiple parameter.

        @param topiks            QuerySet<topik> objects.

        Optional parameter:
        @param bidang               (String) short of Bidang.
        @param ketersediaan         (String) Tersedia or Tidak Tersedia.
        @param pengerjaan           (Integer) 1 - 3.

        @return QuerySet<topik> contains result of filtered topiks.
        """
        if topiks is None:
            topiks = Topik.objects.all()

        topiks = TopikFilter.__filter_by_bidang(topiks, **kwargs)
        topiks = TopikFilter.__filter_by_ketersediaan(topiks, **kwargs)
        topiks = TopikFilter.__filter_by_pengerjaan(topiks, **kwargs)
        return topiks
