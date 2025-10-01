from django.urls import path
from . import views

urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('external/register/', views.register_external_user, name='register_external'),
    path('external/search/', views.search_external_users, name='search_external'),
    path('external/<int:user_id>/approve/', views.approve_external_user, name='approve_external'),
]