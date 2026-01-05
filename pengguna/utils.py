# pengguna/utils.py atau views.py
from django.contrib.auth.models import Group
from .models import User

def assign_role_to_user(user, role_name):
    # Memastikan group/role ada di database
    group, _ = Group.objects.get_or_create(name=role_name)
    user.groups.add(group)

def pendaftaran_otomatis(email, password, role_yang_dipilih):
    # 1. Cari atau buat user
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0],
        }
    )
    
    # 2. Set password jika user baru
    if created:
        user.set_password(password)
        user.save()
    
    # 3. Tambahkan role baru (tanpa menghapus role lama)
    assign_role_to_user(user, role_yang_dipilih)
    
    return user