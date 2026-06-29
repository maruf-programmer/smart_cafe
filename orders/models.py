from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import MenuItem, Table


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Naqd pul'),
        ('card', 'Karta'),
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('uzum', 'Uzum Bank'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Kutilmoqda'),
        ('success', 'Muvaffaqiyatli'),
        ('failed', 'Rad etildi'),
        ('refunded', 'Qaytarildi'),
    ]

    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment', verbose_name='Buyurtma')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Summa')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash', verbose_name='To\'lov turi')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name='Holat')
    transaction_id = models.CharField(max_length=200, blank=True, verbose_name='Tranzaksiya ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Sana')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Yakunlangan')

    class Meta:
        verbose_name = 'To\'lov'
        verbose_name_plural = 'To\'lovlar'

    def __str__(self):
        return f"{self.order} - {self.amount} so'm ({self.get_status_display()})"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlandi'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('delivered', 'Yetkazildi'),
        ('completed', 'Yakunlandi'),
        ('cancelled', 'Bekor qilindi'),
    ]

    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name='orders', verbose_name='Stol')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Holat')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Jami narx")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Yakunlangan vaqt')
    notes = models.TextField(blank=True, verbose_name='Eslatma')

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"Buyurtma #{self.id} - Stol {self.table.number}"

    def update_total(self):
        self.total_price = sum(item.subtotal for item in self.items.all())
        self.save()

    def complete_order(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        self.table.free_table()

    def mark_delivered(self):
        self.status = 'delivered'
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Buyurtma')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, verbose_name='Taom')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Soni')
    servings = models.IntegerField(default=1, verbose_name='Kishilik')
    price_per_serving = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Bir kishilik narx')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Jami')
    notes = models.TextField(blank=True, verbose_name='Qo\'shimcha')

    class Meta:
        verbose_name = 'Buyurtma elementi'
        verbose_name_plural = 'Buyurtma elementlari'

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price_per_serving * self.quantity * self.servings
        super().save(*args, **kwargs)


class WaiterCall(models.Model):
    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name='waiter_calls', verbose_name='Stol')
    reason = models.CharField(max_length=200, blank=True, verbose_name='Sabab')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Chaqirilgan vaqt')
    is_answered = models.BooleanField(default=False, verbose_name='Javob berildi')
    answered_at = models.DateTimeField(null=True, blank=True, verbose_name='Javob vaqti')
    reply_message = models.TextField(blank=True, verbose_name='Javob xabari')
    staff_phone = models.CharField(max_length=20, blank=True, verbose_name='Xodim telefoni')

    class Meta:
        verbose_name = 'Ofitsiant chaqiruvi'
        verbose_name_plural = 'Ofitsiant chaqiruvlari'
        ordering = ['-created_at']

    def __str__(self):
        answered = "Javob berildi" if self.is_answered else "Kutilmoqda"
        return f"Stol {self.table.number} - {answered}"

    def send_sms_notification(self):
        """Simulyatsiya qilingan SMS yuborish"""
        self.staff_phone = '+998901234567'
        self.save()
        return f"SMS yuborildi"

    def reply_with_message(self, message):
        """Mijozga javob yuborish"""
        self.reply_message = message
        self.is_answered = True
        self.answered_at = timezone.now()
        self.save()
        return True


class TableMessage(models.Model):
    SENDER_CHOICES = [
        ('customer', 'Mijoz'),
        ('staff', 'Xodim'),
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='messages', verbose_name='Stol')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES, default='customer', verbose_name='Yuboruvchi')
    message = models.TextField(verbose_name='Xabar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yuborilgan vaqt')
    is_read = models.BooleanField(default=False, verbose_name='O\'qildi')

    class Meta:
        verbose_name = 'Stol xabari'
        verbose_name_plural = 'Stol xabarlari'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.upper()} - Stol {self.table.number}: {self.message[:20]}"
