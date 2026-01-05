# pengguna/models.py
from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class User(AbstractUser):
    """
    Model User kustom untuk mendukung login menggunakan email
    dan sistem multiple roles menggunakan Django Groups.
    """
    email = models.EmailField(unique=True, verbose_name="Alamat Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="No. WhatsApp")
    
    # Metadata tambahan (opsional)
    bio = models.TextField(blank=True, null=True, help_text="Khusus untuk profil Instruktur")
    foto_profil = models.ImageField(upload_to='profil/', blank=True, null=True)

    # Konfigurasi agar email menjadi identitas login utama
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Pengguna"
        verbose_name_plural = "Pengguna"

    def __str__(self):
        return self.email

    # --- Helper Methods untuk Mengecek Role ---
    
    @property
    def is_admin(self):
        return self.groups.filter(name='Admin').exists()

    @property
    def is_instruktur(self):
        return self.groups.filter(name='Instruktur').exists()

    @property
    def is_finance(self):
        return self.groups.filter(name='Finance').exists()

    @property
    def is_peserta(self):
        return self.groups.filter(name='Peserta').exists()

    @property
    def get_all_roles(self):
        """Mengembalikan daftar semua role yang dimiliki user"""
        return list(self.groups.values_list('name', flat=True))

class UserProfile(models.Model):
    """
    Model tambahan jika Anda ingin memisahkan data spesifik antara
    peserta dan instruktur di masa depan.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    instansi = models.CharField(max_length=255, blank=True, null=True)
    alamat_lengkap = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profil: {self.user.email}"