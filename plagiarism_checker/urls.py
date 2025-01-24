from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from codes import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Простая домашняя страница
def home(request):
    return HttpResponse("Welcome to Plagiarism Checker!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('codes.urls')),  # Подключаем urls из приложения codeChecker
    path('app/upload/', views.app_upload, name='app_upload'),  # Страница для загрузки кода
    path('app/results/', views.app_results, name='app_results'),  # Страница для вывода результатов
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # API для получения токена
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # API для обновления токена
    path('api/', include('codes.urls')),  # Подключение API для расширенного функционала
    path('', views.index, name='index'),  # Главная страница
    path('login/', views.user_login, name='login'),  # Страница логина
]
