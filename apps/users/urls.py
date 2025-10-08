from apps import users
from apps.users import views
from django.urls import path

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
]
