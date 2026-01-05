# pengguna/urls.py
from django.urls import path
from . import views

app_name = 'pengguna'

urlpatterns = [
    # --- Autentikasi Dasar ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # --- Alur Password Reset ---
    path('password-reset/', views.reset_password_view, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),

    # --- Khusus Login Google ---
    # Halaman ini dipanggil oleh adapter.py setelah user sukses login google tapi belum punya role
    path('pilih-role-google/', views.pilih_role_google, name='pilih_role_google'),

    # --- Manajemen Pengguna (CRUD - Admin Only) ---
    path('users/', views.user_list, name='user_list'),
    path('users/save/', views.user_save, name='user_save'),
    path('users/detail/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
]