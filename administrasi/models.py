from django.db import models
from django.utils import timezone
from decimal import Decimal

class Customer(models.Model):
    """Model untuk Database Pelanggan (CRM)"""
    name = models.CharField(max_length=200, verbose_name="Nama Penerima")
    company = models.CharField(max_length=200, blank=True, verbose_name="Nama Perusahaan")
    email = models.EmailField(unique=True)
    whatsapp = models.CharField(max_length=20, help_text="Format: 628123456789")
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pelanggan"
        verbose_name_plural = "Pelanggan"

    def __str__(self):
        return f"{self.name} ({self.company})" if self.company else self.name


class DocumentType(models.Model):
    """Model untuk Jenis Surat (INV, UM, PKS, dll) dan Template Word-nya"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    template_docx = models.FileField(upload_to='templates/docs/', help_text="Upload template .docx")

    class Meta:
        verbose_name = "Jenis Surat"
        verbose_name_plural = "Jenis Surat"

    def __str__(self):
        return f"{self.name} - {self.code}"


class Correspondence(models.Model):
    """Model Utama Manajemen Surat dan Penomoran"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT, verbose_name="Jenis Surat")
    
    number = models.PositiveIntegerField(editable=False)
    formatted_number = models.CharField(max_length=100, unique=True, editable=False)
    
    subject = models.CharField(max_length=255, verbose_name="Perihal")
    
    file_pdf = models.FileField(upload_to='generated/pdf/', null=True, blank=True)
    file_docx = models.FileField(upload_to='generated/docx/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Arsip Surat"
        verbose_name_plural = "Arsip Surat"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.id:
            now = timezone.now()
            # 1. Logika Reset Nomor tiap Tahun
            last_doc = Correspondence.objects.filter(
                created_at__year=now.year
            ).order_by('-number').first()
            
            self.number = (last_doc.number + 1) if last_doc else 1
            
            # 2. Logika Bulan Romawi
            romans = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
            month_rom = romans[now.month]
            
            # 3. Format: 001/INV/DIGINUS/IX/2026
            self.formatted_number = f"{str(self.number).zfill(3)}/{self.doc_type.code}/DIGINUS/{month_rom}/{now.year}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.formatted_number


class Invoice(models.Model):
    TYPE_CHOICES = [('DP', 'Down Payment'), ('LUNAS', 'Pelunasan')]
    
    correspondence = models.OneToOneField(Correspondence, on_delete=models.CASCADE, related_name='invoice_detail')
    invoice_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='LUNAS')
    
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0) 
    is_paid = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)

    @property
    def subtotal(self):
        """Total murni dari semua item sebelum pajak"""
        return sum(item.subtotal for item in self.items.all())

    @property
    def tax_amount(self):
        """Nilai PPN 11%"""
        # Kita gunakan Decimal untuk akurasi keuangan
        return (self.subtotal * Decimal('0.11')).quantize(Decimal('1.00'))

    @property
    def grand_total(self):
        """Total yang harus dibayar (Subtotal + PPN)"""
        return self.subtotal + self.tax_amount

    @property
    def remaining_balance(self):
        """Sisa piutang setelah dikurangi pembayaran"""
        return self.grand_total - self.paid_amount

    def __str__(self):
        return f"Inv: {self.correspondence.formatted_number}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return Decimal(self.quantity) * self.unit_price

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.unit_price})"


class Expense(models.Model):
    """Pencatatan Pengeluaran Operasional dan Gaji"""
    CATEGORY_CHOICES = [
        ('GAJI', 'Gaji Karyawan'),
        ('OPERASIONAL', 'Biaya Operasional'),
        ('PAJAK', 'Pajak'),
        ('SEDEKAH', 'Sedekah'),
        ('LAINNYA', 'Lain-lain'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pengeluaran"
        verbose_name_plural = "Pengeluaran"
        ordering = ['-date']

    def __str__(self):
        return f"[{self.category}] {self.title} - Rp {self.amount}"

    @classmethod
    def get_financial_report(cls, month=None, year=None):
        """
        Logika inti untuk rekapitulasi 40/50/10
        """
        from django.db.models import Sum
        
        # Default ke bulan dan tahun berjalan jika tidak diisi
        now = timezone.now()
        month = month or now.month
        year = year or now.year

        # Ambil total pendapatan (dari Invoice yang sudah dibayar)
        total_income = Invoice.objects.filter(
            correspondence__created_at__month=month,
            correspondence__created_at__year=year,
            is_paid=True
        ).aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')

        # Ambil total pengeluaran
        total_expense = cls.objects.filter(
            date__month=month,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Hitung Net Profit
        net_profit = total_income - total_expense

        # Alokasi (40/50/10)
        return {
            'revenue': total_income,
            'expenses': total_expense,
            'net_profit': net_profit,
            'allocation_gaji': net_profit * Decimal('0.40') if net_profit > 0 else 0,
            'allocation_ops': net_profit * Decimal('0.50') if net_profit > 0 else 0,
            'allocation_sedekah': net_profit * Decimal('0.10') if net_profit > 0 else 0,
        }