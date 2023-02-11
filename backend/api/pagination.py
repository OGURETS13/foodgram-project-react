from rest_framework import pagination


class PageNumberAndLimitPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
