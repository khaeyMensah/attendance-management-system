from django.urls import path

from apps.attendance import views

app_name = 'attendance'

urlpatterns = [
    path('join/', views.enter_code_view, name='enter_code'),
    path('scan/<str:qr_token>/', views.scan_qr_view, name='scan_qr'),
    path('my-history/', views.my_attendance_view, name='my_attendance'),
    path('session/start/<int:course_id>/', views.start_session_view, name='start_session'),
    path('session/<int:session_id>/qr/', views.session_qr_view, name='session_qr'),
    path('session/<int:session_id>/records/', views.session_records_view, name='session_records'),
    path('session/<int:session_id>/close/', views.close_session_view, name='close_session'),
]
