from django.db import models
from django.utils import timezone


class Staff(models.Model):
    ROLE_CHOICES = [
        ('waiter', 'Ofitsiant'),
        ('chef', 'Oshpaz'),
        ('admin', 'Administrator'),
        ('cleaner', 'Farrosh'),
    ]

    name = models.CharField(max_length=100, verbose_name='Ism')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='waiter', verbose_name='Lavozim')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    qr_code = models.CharField(max_length=200, blank=True, verbose_name='QR kod (URL)')

    class Meta:
        verbose_name = 'Xodim'
        verbose_name_plural = 'Xodimlar'
        ordering = ['role', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    def send_sms(self, message):
        print(f"[SMS] {self.phone} -> {message}")
        return True


class Table(models.Model):
    STATUS_CHOICES = [
        ('free', 'Bo\'sh'),
        ('occupied', 'Band'),
        ('reserved', 'Bron qilingan'),
        ('cleaning', 'Tozalanmoqda'),
    ]

    number = models.IntegerField(unique=True, verbose_name='Stol raqami')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free', verbose_name='Holat')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    qr_code = models.CharField(max_length=200, blank=True, verbose_name='QR kod (URL)')
    current_session_start = models.DateTimeField(null=True, blank=True, verbose_name='Joriy sessiya boshlanishi')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Stol'
        verbose_name_plural = 'Stollar'
        ordering = ['number']

    def __str__(self):
        return f"Stol #{self.number} ({self.get_status_display()})"

    def occupy(self):
        self.status = 'occupied'
        self.current_session_start = timezone.now()
        self.save()

    def free_table(self):
        self.status = 'cleaning'
        self.current_session_start = None
        self.save()

    def mark_free(self):
        self.status = 'free'
        self.save()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:select_table', kwargs={'table_id': self.id})


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Kategoriya nomi')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    image = models.CharField(max_length=200, blank=True, verbose_name='Rasm (URL)')
    prep_time_minutes = models.IntegerField(default=15, verbose_name="Pishirish vaqti (daqiqa)")
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    order = models.IntegerField(default=0, verbose_name='Tartib')

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=200, verbose_name='Taom nomi')
    description = models.TextField(verbose_name="Taom haqida")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', verbose_name='Kategoriya')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Narxi (so\'m)')
    image = models.CharField(max_length=200, blank=True, verbose_name='Rasm (URL)')
    images = models.JSONField(default=list, blank=True, verbose_name='Rasmlar ro\'yxati')
    is_available = models.BooleanField(default=True, verbose_name='Mavjud')
    prep_time_minutes = models.IntegerField(default=20, verbose_name="Tayyorlash vaqti (daqiqa)")
    serving_options = models.JSONField(default=list, blank=True, verbose_name='Porsiya turlari')
    ingredients = models.TextField(blank=True, verbose_name='Tarkibi')
    vitamins = models.CharField(max_length=500, blank=True, verbose_name='Vitaminlar')
    weight_grams = models.IntegerField(default=250, verbose_name='Og\'irligi (g)')
    calories = models.IntegerField(default=0, verbose_name='Kaloriya')
    is_popular = models.BooleanField(default=False, verbose_name='Mashhur')

    class Meta:
        verbose_name = 'Taom'
        verbose_name_plural = 'Taomlar'
        ordering = ['category__order', 'name']

    def __str__(self):
        return self.name

    @property
    def prep_time_display(self):
        hours = self.prep_time_minutes // 60
        minutes = self.prep_time_minutes % 60
        if hours > 0:
            return f"{hours} soat {minutes} daq"
        return f"{minutes} daq"


class Advertisement(models.Model):
    title = models.CharField(max_length=200, verbose_name='Sarlavha')
    description = models.TextField(blank=True, verbose_name='Matn')
    image = models.CharField(max_length=200, blank=True, verbose_name='Rasm (URL)')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    display_order = models.IntegerField(default=0, verbose_name='Ko\'rsatish tartibi')
    link = models.URLField(blank=True, null=True, verbose_name='Havola')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reklama'
        verbose_name_plural = 'Reklamalar'
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title
