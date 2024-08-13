from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

class CustomUser(AbstractUser):
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True)
    gender = models.CharField(_('gender'), max_length=6, choices=GENDER_CHOICES, blank=True)
    province = models.CharField(_('province'), max_length=255, blank=True)
    district = models.CharField(_('district'), max_length=255, blank=True)
    tole = models.CharField(_('tole'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')



class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class RootCategory(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='root_category')
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.category.name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image1 = models.ImageField(upload_to='product_images/')
    image2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    available_quantity = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'product'


User = get_user_model()
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Cart #{self.pk} - User: {self.user}"

    class Meta:
        db_table = 'cart'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Cart #{self.cart.pk}"

    class Meta:
        db_table = 'cart_item'


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered_items = models.ManyToManyField('Product', through='OrderItem')
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.pk} - User: {self.user}, Status: {self.status}"
    
    class Meta:
        db_table = 'order'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Order #{self.order.pk}"

    class Meta:
        db_table = 'orderitem'

class FavoriteItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.product.title}"

    class Meta:
        unique_together = ['user', 'product']
        db_table = 'favorite_item'


