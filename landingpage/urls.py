from django.urls import path
from . import views

app_name = 'landingpage'

urlpatterns = [
    path('', views.index, name='index'),
    # Halaman Utama Dashboard (Template)
    path('projects/', views.project_list, name='project_list'),
    
    # API Data (Digunakan oleh fungsi loadProjects() di JS)
    path('api/projects/', views.get_projects, name='get_projects'),
    
    # Actions (Proses data AJAX)
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/edit/<int:pk>/', views.project_edit, name='project_edit'),
    path('projects/delete/<int:pk>/', views.project_delete, name='project_delete'),
]