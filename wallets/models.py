from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Wallet(models.Model):
    """Модель кошелька."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet {self.id}"

    class Meta:
        verbose_name = "Кошелек"
        verbose_name_plural = "Кошельки"
        ordering = ('id',)


class Operation(models.Model):
    """Модель выполняемой опрерации."""

    OPERATION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='operations'
        )
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Operation {self.id}"

    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "Операции"
        ordering = ('id',)
