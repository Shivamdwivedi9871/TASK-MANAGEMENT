from rest_framework.pagination import CursorPagination, PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework import status


class FavoriteCursorPagination(CursorPagination):
    page_size = 20
    ordering = "id"  # Newest favorites first
    cursor_query_param = "cursor"

    def get_paginated_response(self, results, meta=None):
        meta = meta or {}
        print('DATA TYPE:', type(results))
        print('META TYPE:', type(meta))
        print('META DATA:', meta)
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': results,
            'meta': meta
        })


class FavoritePageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = None
    page_query_param = "page"

    def get_paginated_response(self, data):
        total_itmes = self.page.paginator.count
        page_size = self.page.paginator.per_page
        page = self.page.number
        total_pages = self.page.paginator.num_pages
        return Response({
            "pagination": {
                "page": page,
                "page_Size": page_size,
                "total_items": total_itmes,
                "total_pages": total_pages,
                "next_page": page + 1 if page_size < total_pages else {"error": "Page not found", "status": status.HTTP_404_NOT_FOUND},
                "previous_page": page - 1 if (page > 1) else {"error": "Page not found", "status": status.HTTP_404_NOT_FOUND}
            },
            "result": data
        })


class FavoriteLimitOffset(LimitOffsetPagination):
    default_limit = 20
    limit_query_param = "limit"
    offset_query_param = "offset"
    max_limit = 50
