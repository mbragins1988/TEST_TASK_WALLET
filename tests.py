from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from wallets.models import Wallet
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from django.db import connection


class WalletAPITests(APITestCase):

    def setUp(self):
        """Настройка тестовых данных."""
        self.wallet = Wallet.objects.create(balance=1000)
        self.wallet_url = reverse(
            'wallet-detail', kwargs={'pk': self.wallet.id}
            )
        self.operation_url = reverse(
            'wallet-operation', kwargs={'pk': self.wallet.id}
        )

    def test_create_wallet_via_api(self):
        """Cоздание кошелька."""

        url = reverse('wallet-list')
        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['balance'], '0.00')

    def test_get_wallet_balance(self):
        """Получение баланса кошелька."""

        response = self.client.get(self.wallet_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '1000.00')

    def test_deposit_operation(self):
        """Пополнение кошелька."""

        data = {
            'operation_type': 'DEPOSIT',
            'amount': '500.00'
        }
        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '1500.00')  # 1000 + 500

    def test_withdraw_operation(self):
        """Снятие средств."""

        data = {
            'operation_type': 'WITHDRAW',
            'amount': '500.00'
        }

        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '500.00')  # 1000 - 500

    def test_withdraw_insufficient_funds(self):
        """Снятие при недостатке средств."""

        data = {
            'operation_type': 'WITHDRAW',
            'amount': '5000.00'
        }

        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Недостаточно денежных средств', response.data['error'])

    def test_invalid_operation_type(self):
        """Неверный тип операции."""

        data = {
            'operation_type': 'INVALID',
            'amount': '500.00'
        }

        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'is not a valid choice', str(response.data['operation_type'])
            )

    def test_negative_amount(self):
        """Ввели отрицательную сумму."""

        data = {
            'operation_type': 'DEPOSIT',
            'amount': '-500.00'
        }

        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn(
            'Сумма не может быть отрицательной', response.data.get('amount')
            )

    def test_zero_amount(self):
        """Ввели нулевое значение."""

        data = {
            'operation_type': 'DEPOSIT',
            'amount': '0.00'
        }

        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'Сумма не может быть нулевой', response.data.get('amount')
            )

    def test_nonexistent_wallet(self):
        """Запрос к несуществующему кошельку."""

        from uuid import uuid4
        fake_wallet_id = uuid4()  # Создает случайный UUID
        url = reverse('wallet-operation', kwargs={'pk': fake_wallet_id})

        response = self.client.post(url, {
            'operation_type': 'DEPOSIT',
            'amount': '500.00'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WalletConcurrencyTests(TransactionTestCase):
    """Тесты конкурентности операций с кошельком."""

    def setUp(self):
        self.wallet = Wallet.objects.create(balance=1000)
        self.operation_url = reverse(
            'wallet-operation', kwargs={'pk': self.wallet.id}
            )

    def test_concurrent_operations(self):
        """Вызываем два параллельных запроса."""

        from concurrent.futures import ThreadPoolExecutor

        def make_deposit():
            """Пополнить средства."""

            self.client = APIClient()
            try:
                # Создаем нового клиента для этого потока
                response = self.client.post(
                    self.operation_url,
                    {'operation_type': 'DEPOSIT', 'amount': '500.00'},
                    format='json'
                )
                return response
            finally:
                connection.close()

        def make_withdraw():
            """Снять средства."""

            self.client = APIClient()
            try:
                # Создаем нового клиента для этого потока
                response = self.client.post(
                    self.operation_url,
                    {'operation_type': 'WITHDRAW', 'amount': '300.00'},
                    format='json'
                )
                return response
            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(make_deposit)
            future2 = executor.submit(make_withdraw)

            response1 = future1.result()
            response2 = future2.result()

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.wallet.refresh_from_db()
        # Итоговый баланс после всех операций
        self.wallet.refresh_from_db()  # Обновление объекта
        # 1000 + 500 - 300 = 1200
        self.assertEqual(str(self.wallet.balance), '1200.00')
