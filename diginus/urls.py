from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include  # ← tambahkan include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landingpage.urls')),
    path('program/', include('program.urls')),
    path('courses/', include('courses.urls')),
    path('administrasi/', include('administrasi.urls')),
    path('pengguna/', include('pengguna.urls')),
    path('accounts/', include('allauth.urls')),
]

# Tambahkan ini hanya saat development
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)