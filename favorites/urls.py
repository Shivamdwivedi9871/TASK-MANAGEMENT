from django.urls import path
from .views import FavoriteListCreateView, FavoriteDetailView, BookView, JwtLogin, AccessTokenFromRefreshToken, BookViewDetails
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('books/', FavoriteListCreateView.as_view(), name='book-list'),
    path('books/<int:pk>/', FavoriteDetailView.as_view(), name='book-details'),
    path('profile/', BookView.as_view(), name='profile'),
    path('profile/obtain_token/', obtain_auth_token, name='obtain_token'),
    path('create_token/', JwtLogin.as_view(), name='Jwt_Token'),
    path('refresh_token/', AccessTokenFromRefreshToken.as_view(), name='refres_token'),
    path('info/', BookViewDetails.as_view(), name='data'),
]
