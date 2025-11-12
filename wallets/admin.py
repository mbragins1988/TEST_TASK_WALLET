from django.contrib import admin
from wallets.models import Operation, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'balance',
    )


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'wallet',
    )
