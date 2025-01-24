from django.urls import path
from . import views

urlpatterns = [
    # Путь для страницы отправки кода
    path('', views.submit_code, name='submit_code'),

    # Путь для страницы результатов проверки кода
    path('results/', views.results, name='result_page'),

    # Путь для загрузки работы
    path('upload/', views.app_upload, name='app_upload'),

    # Путь для отображения всех результатов
    path('results/', views.app_results, name='app_results'),

    # Путь для страницы входа
    path('login/', views.user_login, name='login'),

    path('submit_code/', views.submit_code, name='submit_code'),

]
