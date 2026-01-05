from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpResponseForbidden
from .models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.hashers import make_password

# --- DECORATOR KHUSUS ADMIN ---
def admin_only(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses halaman ini.")
    return wrap

# --- AUTHENTICATION VIEWS ---

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        role_pilihan = request.POST.getlist('roles')

        if User.objects.filter(email=email).exists():
            return render(request, 'pengguna/signup.html', {'error': 'Email sudah terdaftar'})

        user = User.objects.create(
            email=email,
            username=email.split('@')[0],
            first_name=nama,
            password=make_password(password)
        )

        for role_name in role_pilihan:
            group, _ = Group.objects.get_or_create(name=role_name)
            user.groups.add(group)

        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/')
        
    return render(request, 'pengguna/signup.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if user.is_superuser or user.groups.filter(name='Admin').exists():
                return redirect('administrasi:finance_dashboard') # Admin ke Manajemen User
            
            elif user.groups.filter(name='Finance').exists():
                return redirect('administrasi:correspondence_list')
            
            elif user.groups.filter(name='Instruktur').exists():
                return redirect('/dashboard-instruktur/') # Ganti dengan URL instruktur Anda
            
            elif user.groups.filter(name='Peserta').exists():
                return redirect('/dashboard-peserta/') #
            
            else:
                return redirect('/') # Default jika tidak ada role khusus
            
    else:
        form = AuthenticationForm()
    return render(request, 'pengguna/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('pengguna:login')

# --- PASSWORD RESET FLOW ---

def reset_password_view(request):
    return auth_views.PasswordResetView.as_view(
        template_name='pengguna/password_reset.html',
        email_template_name='pengguna/password_reset_email.html',
        success_url='/pengguna/password-reset/done/'
    )(request)

def password_reset_done(request):
    return render(request, 'pengguna/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    return auth_views.PasswordResetConfirmView.as_view(
        template_name='pengguna/password_reset_confirm.html',
        success_url='/pengguna/password-reset/complete/'
    )(request, uidb64=uidb64, token=token)

def password_reset_complete(request):
    return render(request, 'pengguna/password_reset_complete.html')

# --- GOOGLE ROLE SELECTION ---

@login_required
def pilih_role_google(request):
    if request.user.groups.exists():
        return redirect('/')

    if request.method == 'POST':
        roles_terpilih = request.POST.getlist('roles')
        if roles_terpilih:
            for role_name in roles_terpilih:
                if role_name in ['Peserta', 'Instruktur']:
                    group, _ = Group.objects.get_or_create(name=role_name)
                    request.user.groups.add(group)
            return redirect('/')
            
    return render(request, 'pengguna/pilih_role_google.html')

# --- USER CRUD (ADMIN ONLY) ---

@login_required
@admin_only
def user_list(request):
    users = User.objects.all().prefetch_related('groups')
    groups = Group.objects.all()
    return render(request, 'pengguna/user_list.html', {'users': users, 'groups': groups})

@login_required
@admin_only
def user_save(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        # Menghapus '[]' agar konsisten dengan AJAX standar
        role_names = request.POST.getlist('roles') 

        if user_id:
            user = get_object_or_404(User, id=user_id)
            user.email = email
            user.first_name = first_name
            if password: user.set_password(password)
        else:
            user = User(email=email, username=email.split('@')[0], first_name=first_name)
            user.set_password(password)
        
        user.save()
        user.groups.set(Group.objects.filter(name__in=role_names))
        return JsonResponse({'status': 'success'})

@login_required
@admin_only
def user_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(User, pk=pk).delete()
        return JsonResponse({'status': 'success'})

@login_required
@admin_only
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return JsonResponse({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'roles': list(user.groups.values_list('name', flat=True))
    })