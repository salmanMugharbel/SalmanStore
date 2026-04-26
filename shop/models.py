from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    name = models.CharField(max_length=120)
    price = models.FloatField()
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='orders'
    )
    quantity = models.IntegerField()
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id}'
