from rest_framework import serializers
from .models import Wallet, Operation
from decimal import Decimal


class OperationSerializer(serializers.Serializer):
    operation_type = serializers.ChoiceField(choices=Operation.OPERATION_TYPES)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        """Валидация для amount."""

        if value < Decimal('0'):
            raise serializers.ValidationError(
                "Сумма не может быть отрицательной"
                )
        elif value == Decimal('0'):
            raise serializers.ValidationError("Сумма не может быть нулевой")
        return value


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'created_at', 'updated_at']
