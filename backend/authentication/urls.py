from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('check-auth/', views.check_auth_status, name='check_auth'),
    path('token/refresh/', views.refresh_token, name='token_refresh'),
    path('token/verify/', views.verify_token, name='token_verify'),
]