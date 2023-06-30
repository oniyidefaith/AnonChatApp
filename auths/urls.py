from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import consumers
from django.views.generic import TemplateView


urlpatterns = [
    path('', views.login, name='login'),
    path('register', views.register, name='register'),
    path('link', views.link_view, name='link'),
    path('room/<str:room_name>/', views.room_view, name='room'),
]
