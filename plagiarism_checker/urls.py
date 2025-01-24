from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from codes import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def home(request):
    return HttpResponse("Welcome to Plagiarism Checker!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', views.app_upload),  # Страница для загрузки кода
    path('app/results/', views.app_results),  # Страница для вывода результатов
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('codes.urls')),  # Подключение API для расширенного функционала
    path('', views.index, name='index'),  # или любая другая страница
    path('upload/', views.app_upload, name='app_upload'),
    path('results/', views.app_results, name='app_results'),
    path('login/', views.user_login, name='login'),
]



