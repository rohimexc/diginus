from django.db import models
class ProjectDone(models.Model):
    title = models.CharField(max_length=100, help_text="Nama Perusahaan atau Nama Projek")
    logo = models.ImageField(upload_to='projects/logos/', help_text="Upload logo transparan (format PNG/SVG direkomendasikan)")
    description = models.TextField(blank=True, null=True, help_text="Deskripsi singkat projek (opsional)")
    url = models.URLField(blank=True, null=True, help_text="Link ke website klien atau detail projek (opsional)")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Urutan tampilan (angka kecil muncul lebih dulu)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Projek Selesai"
        verbose_name_plural = "Daftar Projek Selesai"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title