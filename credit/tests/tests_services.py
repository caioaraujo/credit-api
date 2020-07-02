from django.test import TestCase
from model_mommy import mommy

from ..exceptions import LoanException
from ..models import Loan
from ..services import LoanService


class TestLoanService(TestCase):

    def _data_input(self):
        return {
            'name': 'Test',
            'cpf': '11122233309',
            'birthdate': '1980-01-01',
            'amount': '1290.90',
            'terms': 6,
            'income': '5000.00',
        }

    def test_insert_success(self):
        service = LoanService()

        result = service.insert(self._data_input())

        self.assertIsInstance(result, Loan)
        self.assertIsNotNone(result.id)

    def test_insert_required_fields(self):
        required_field_error = 'Required field'
        service = LoanService()

        with self.assertRaises(LoanException) as exc:
            service.insert({})

        errors = exc.exception.args[0]
        self.assertIn({'name': required_field_error}, errors)
        self.assertIn({'cpf': required_field_error}, errors)
        self.assertIn({'birthdate': required_field_error}, errors)
        self.assertIn({'amount': required_field_error}, errors)
        self.assertIn({'terms': required_field_error}, errors)
        self.assertIn({'income': required_field_error}, errors)

    def test_insert_amount_out_of_limit(self):
        service = LoanService()
        data = self._data_input()
        data['amount'] = '999.99'

        with self.assertRaises(LoanException) as exc:
            service.insert(data)

        errors = exc.exception.args[0]
        self.assertIn({'amount': 'Out of limit allowed'}, errors)

    def test_get_loans_in_process(self):
        mommy.make('Loan', status='processing', _quantity=3)
        mommy.make('Loan', status='completed', _quantity=5)

        service = LoanService()
        result = service.get_loans_in_process()
        self.assertEqual(3, len(result))
        [self.assertEqual('processing', loan.status) for loan in result]
