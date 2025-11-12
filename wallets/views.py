from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Wallet
from .serializers import WalletSerializer, OperationSerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

    # Запрещаем получение списка кошельков
    def list(self, request, *args, **kwargs):
        return Response(
            {"error": "Нельзя смотреть все кошельки"},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=['post'])
    def operation(self, request, pk):
        """Операции с кошельком."""

        serializer = OperationSerializer(data=request.data)
        print('request.data', request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        # Создается транзакция
        with transaction.atomic():
            # Блокируем кошелек для этого запроса
            wallet = get_object_or_404(
                Wallet.objects.select_for_update(),
                pk=pk
            )
            operation_type = serializer.validated_data['operation_type']
            amount = serializer.validated_data['amount']

            if operation_type == 'WITHDRAW':
                if wallet.balance < amount:
                    return Response({
                        'error': f'''Недостаточно денежных средств,
                                  доступно {wallet.balance}'''},
                        status=400)
                wallet.balance -= amount
            else:
                wallet.balance += amount
            wallet.save()
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)
