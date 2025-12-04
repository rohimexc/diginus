from django.urls import path
from . import views

app_name = 'program'

urlpatterns = [
    path('', views.index, name='index'),
    path('datatables/', views.ProgramDataTablesView.as_view(), name='datatables'),
    path('create-or-update/', views.create_or_update_program, name='create_or_update'),
    path('delete/', views.delete_program, name='delete'),
    path('import/', views.import_program, name='import'),
    path('export/', views.export_program, name='export'),
]