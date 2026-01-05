from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Service(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('creative', 'Creative & Design'),
        ('production', 'Media Production'),
        ('event', 'Event Management'),
        ('consultation', 'Konsultasi'),
        ('development', 'IT Development'),
    ]

    LOCATION_CHOICES = [
        ('online', 'Online/Remote'),
        ('onsite', 'On-site (Lokasi Fisik)'),
        ('hybrid', 'Hybrid'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey('courses.Category', on_delete=models.CASCADE, related_name='services')
    thumbnail = models.ImageField(upload_to='services/thumbnails/')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='creative')
    location_mode = models.CharField(max_length=10, choices=LOCATION_CHOICES, default='online')
    
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_starting_price = models.BooleanField(default=True)
    
    # HAPUS 'placeholder' di sini karena akan menyebabkan TypeError
    estimated_duration = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Contoh: 3 Hari Kerja atau Per Sesi"
    )
    
    managed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_services')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title