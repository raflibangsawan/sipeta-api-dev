from django.core.paginator import EmptyPage, Paginator


class Pagination:
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 25

    def __cleaned_args(self, v, default):
        try:
            return int(v)
        except (ValueError, TypeError):
            return default

    def __init__(self, obj, page=DEFAULT_PAGE, per_page=DEFAULT_PER_PAGE):
        self.page = self.__cleaned_args(page, self.DEFAULT_PAGE)
        self.per_page = self.__cleaned_args(per_page, self.DEFAULT_PER_PAGE)
        self.paginator = Paginator(obj, self.per_page)

    def get_content(self):
        try:
            paginator_page = self.paginator.page(self.page)
            obj = paginator_page.object_list
        except EmptyPage:
            return None, None
        return obj, paginator_page
