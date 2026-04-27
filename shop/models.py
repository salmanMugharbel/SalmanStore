from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='categories', null=True, blank=True
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='products', null=True, blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    name = models.CharField(max_length=120)
    description = models.TextField(default='', blank=True)
    price = models.FloatField()
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='orders'
    )
    quantity = models.IntegerField()
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id}'
