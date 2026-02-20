# from apps import users
from django.urls import path
from apps.users import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

# Add this line to register the namespace used in templates
app_name = 'users'

urlpatterns = [
    # path('', include(('apps.users.urls', 'users'), namespace='users')),
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('lecturer-dashboard/', views.lecturer_dashboard_view, name='lecturer_dashboard'),
    
    path('register/', views.register_view, name='register'),
    path('register-options/', views.register_options, name='register_options'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Account activation urls
    # path('activate/<uidb64>/<token>/', views.activate, name='activate'),  
    path('registration_pending/', TemplateView.as_view(template_name='authentication/registration_pending.html'), name='registration_pending'),  
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activation_success/', TemplateView.as_view(template_name='authentication/activation_success.html'), name='activation_success'),  
    path('activation_invalid/', TemplateView.as_view(template_name='authentication/activation_invalid.html'), name='activation_invalid'),  
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset_form.html'), name='password_reset'), 
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),  
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),  
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'), 

    # Password Change URLs
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change_form.html'), name='password_change'),  
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'), name='password_change_done'),  
]
