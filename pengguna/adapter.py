# pengguna/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        # Jika user baru saja daftar (belum punya Group/Role)
        if not user.groups.exists():
            return reverse('pengguna:pilih_role_google')
        return super().get_login_redirect_url(request)