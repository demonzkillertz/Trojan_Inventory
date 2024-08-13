from django.contrib import admin
from .models import Order, OrderItem , Product, Category, RootCategory

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(RootCategory)
admin.site.register(Category)