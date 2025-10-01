from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_attendance, name='register_attendance'),
    path('stats/', views.get_student_stats, name='student_stats'),
    path('recent/', views.get_recent_attendances, name='recent_attendances'),
]