from django.urls import path

from apps.courses import views

app_name = 'courses'

urlpatterns = [
    path('lecturer/<int:course_id>/', views.lecturer_course_detail_view, name='lecturer_course_detail'),
]
