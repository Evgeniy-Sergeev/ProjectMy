from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.app_upload, name='app_upload'),
    path('results/', views.app_results, name='app_results'),
    path('login/', views.user_login, name='login'),
]
