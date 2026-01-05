from django.urls import path
from . import views

# Memberikan namespace agar bisa dipanggil dengan 'courses:nama_url'
app_name = 'courses'

urlpatterns = [
    # Akses course page
    path('', views.course_page, name='course_list'),
    # Akses category page
    path('categories/', views.category_page, name='category_list'),
    # Kurikulum Page
    path('<int:course_id>/curriculum/', views.course_curriculum_page, name='course_curriculum'),
    
    # --- ENDPOINT CATEGORIES ---
    path('api/categories/', views.api_category_list, name='api_categories_list'),
    path('api/categories/create/', views.api_category_create, name='api_categories_create'),
    path('api/categories/update/<int:pk>/', views.api_category_update, name='api_categories_update'),
    path('api/categories/delete/<int:pk>/', views.api_category_delete, name='api_categories_delete'),

    # --- API ENDPOINTS COURSES ---
    path('api/courses/', views.api_course_list, name='api_course_list'),
    path('api/courses/create/', views.api_course_create, name='api_course_create'),
    path('api/courses/update/<int:pk>/', views.api_course_update, name='api_course_update'),
    path('api/courses/delete/<int:pk>/', views.api_course_delete, name='api_course_delete'),
    
    # Module API
    path('api/courses/<int:course_id>/modules/', views.api_module_list, name='api_module_list'),
    path('api/courses/<int:course_id>/modules/create/', views.api_module_create, name='api_module_create'),
    path('api/modules/delete/<int:pk>/', views.api_module_delete, name='api_module_delete'),
    # Lesson API
    path('api/modules/<int:module_id>/lessons/create/', views.api_lesson_create, name='api_lesson_create'),
    path('api/lessons/delete/<int:pk>/', views.api_lesson_delete, name='api_lesson_delete'),
    
    # QUIZ
    path('modules/<int:module_id>/quiz/', views.quiz_detail_page, name='quiz_manager'),
    path('quiz/<int:quiz_id>/take/', views.quiz_take_page, name='quiz_take'),
    path('api/quiz/<int:quiz_id>/data/', views.api_quiz_data, name='api_quiz_data'),
    path('api/quiz/<int:quiz_id>/question/create/', views.api_question_create, name='api_question_create'),
    path('api/questions/<int:question_id>/answer/add/', views.api_answer_add, name='api_answer_add'),
    path('api/questions/delete/<int:pk>/', views.api_question_delete, name='api_question_delete'),
    path('api/quiz/<int:quiz_id>/submit/', views.api_quiz_submit, name='api_quiz_submit'),
    
    # Project
    path('modules/<int:module_id>/project/', views.project_manager_page, name='project_manager'),
    path('api/projects/<int:pk>/', views.api_project_detail, name='api_project_detail'),
    path('api/projects/<int:pk>/update/', views.api_project_update, name='api_project_update'),
]