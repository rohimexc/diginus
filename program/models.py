from django.db import models


from django.db import models


class Program(models.Model):
    JENIS_CHOICES = [
        ('Courses', 'Courses'),
        ('Services', 'Services'),
    ]

    LEVEL_CHOICES = [
        ('Basic', 'Basic'),
        ('Intermediate', 'Intermediate'),
        ('Advance', 'Advance'),
    ]

    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()
    thumbnail = models.ImageField(upload_to='program_thumbnails/')
    harga = models.DecimalField(max_digits=12, decimal_places=2)
    jenis = models.CharField(max_length=20, choices=JENIS_CHOICES)
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        null=True,
        blank=True,  # agar boleh kosong bila Services
    )

    pendaftaran_mulai = models.DateField(null=True, blank=True)
    pendaftaran_tutup = models.DateField(null=True, blank=True)
    pelaksanaan_mulai = models.DateField(null=True, blank=True)
    pelaksanaan_selesai = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Jika jenis = Services, kosongkan level
        if self.jenis == 'Services':
            self.level = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama

