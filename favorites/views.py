from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import exceptions
from .permissions import IsOwnerOrAdmin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.decorators import login_required
from .serializers import FavoriteSerializer
from .models import Favorite
from .forms import FormFavorite
from .utils import decode_token
from .auth_utils import create_access_token, create_refresh_token
from django.contrib.auth import get_user_model
from .serializers import CategoriesSerializer
from .services import CreateType
from .throttle import PerUserORIPThrottle
from rest_framework import throttling
from .authentication import CustomJwtAuthentication
from django.core.cache import cache
from .tasks import notification_email, test_task
from .paginations import FavoriteCursorPagination, FavoritePageNumberPagination, FavoriteLimitOffset
from django.db.models import Avg, Max
from .services import CustomRateLimit
from .tasks import send_daily_favorite
# Create your views here.

User = get_user_model()


class FavoriteListCreateView(generics.ListCreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['rating', 'owner']
    search_fields = ['title', 'author__name', 'owner__username']
    ordering_fields = ['title', 'rating', 'id']

    def get_queryset(self):
        send_daily_favorite.delay(self.request.user.id)
        return Favorite.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

        notification_email.delay(self.request.user.email)


@login_required
def add_favorite(request):
    if request.method == 'POST':
        form = FormFavorite(self.request.POST)
        if form.is_valid:
            favorite = form.save(commit=False)
            favorite.owner = request.user
            favorite.save()
    else:
        form = FormFavorite()

    return render(request, 'your template.html', {'form': form})


class FavoriteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Favorite.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


class BookView(APIView):
    authentication_classes = [CustomJwtAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [PerUserORIPThrottle]
    throttle_scope = "user"
    pagination_class = FavoriteCursorPagination

    def get(self, request):
        user = request.user
        queryset = Favorite.objects.filter(owner=user).order_by('id')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = FavoriteSerializer(page, many=True)
        results = serializer.data

        # cache_key = f"book{user.id}"

        # meta = cache.get(cache_key)

        # if meta is None:

        meta = {
            'username': user.username,
            'is_staff': user.is_staff
        }

        # cache.set(cache_key, meta, timeout=300)

        print('RESULT:', type(results))
        print('META:', type(meta))

        breakpoint()

        return paginator.get_paginated_response(results, meta=meta)


class JwtLogin(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'details': 'Inavlid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        return Response({
            'access_token': token,
            'token_type': 'Bearer',
            'refresh_token': refresh_token
        })


class AccessTokenFromRefreshToken(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Inavlid Token'}, status=status.HTTP_400_BAD_REQUEST)

        payload = decode_token(refresh_token)

        if not payload:
            return Response({
                'detail': 'Invalid or Expire Token'
            })

        token_type = payload.get('type')

        if token_type != 'refresh':
            return Response({
                'detail': 'Invalid Token'
            }, status=status.HTTP_400_BAD_REQUEST)

        username = payload.get('username')

        if not username:
            return Response({'detail': 'Token Missing username'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            return Response({
                'detail': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        new_access = create_access_token(user)

        return Response(
            {
                'access_token': new_access,
                'token_type': 'bearer',
            },
            status=status.HTTP_201_CREATED
        )


# class CategoryView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [authenticate]

#     def post(self, request, *args, **kwargs):
#         if request.method == 'POST':
#             user = request.user
#             favourite_data = request.data.get('favorite')
#             category_list = request.dat.get('category_list', [])

#             favorite = CreateType.create_category(
#                 user, favourite_data, category_list)

#             return Response({'id': favorite.id}, status=status.HTTP_201_CREATED)


class BookViewDetails(APIView):
    authentication_classes = [CustomJwtAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [PerUserORIPThrottle]
    throttle_scope = "user"
    pagination_class = FavoritePageNumberPagination

    @staticmethod
    def rating_count(result):
        count = {}

        for rating in result:
            count[rating] = count.get(rating, 0)+1
        return count

    def get(self, request):
        user = request.user
        user_id = request.user.id
        allowed = CustomRateLimit.check_rate_limit(user_id)

        if not allowed:
            return Response({
                "details": "Too Many Request"
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        favorite = Favorite.objects.filter(owner=user)
        total = favorite.count()
        highest_rating = favorite.filter(rating__gte=4).count()
        lower_rating = favorite.exclude(rating__gte=2).count()
        # latest_favorite = favorite.order_by("-created_at").values("title", "rating").first()
        rating_status = favorite.aggregate(
            avg_rating=Avg("rating"), max_rating=Max("rating"))
        titles = favorite.values("title")
        title_list = [row["title"] for row in titles]
        results = []
        for fav in favorite:
            results.append(fav.rating or 0)

        stats = self.rating_count(results)

        paginator = self.pagination_class()
        page_qs = paginator.paginate_queryset(favorite, request, view=self)

        page_data = [
            {
                "id": fav.id,
                "title": fav.title,
                "rating": fav.rating
            }
            for fav in page_qs
        ]

        combined_data = {
            "total": total,
            "rating": stats,
            "highest_rating": highest_rating,
            "lower_rating": lower_rating,
            # "latest_favorite":latest_favorite,
            "rating_status": rating_status,
            "title": title_list,
            "itmes": page_data,
        }

        return paginator.get_paginated_response(combined_data)
