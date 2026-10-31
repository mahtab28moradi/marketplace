from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    product = models.OneToOneField(
        Product,
        on_delete=models.PROTECT,
        related_name='order'
    )

    buyer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='purchases'
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sales'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Order #{self.id}"
