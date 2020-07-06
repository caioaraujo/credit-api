from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from kombu.utils import json
from model_mommy import mommy

from ..exceptions import LoanException
from ..models import Loan
from ..services import CreditService, LoanService


class TestLoanService(TestCase):

    def setUp(self):
        self.service = LoanService()

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
        result = self.service.insert(self._data_input())

        self.assertIsInstance(result, Loan)
        self.assertIsNotNone(result.id)

    def test_insert_required_fields(self):
        required_field_error = 'Required field'

        with self.assertRaises(LoanException) as exc:
            self.service.insert({})

        errors = exc.exception.args[0]
        self.assertIn({'name': required_field_error}, errors)
        self.assertIn({'cpf': required_field_error}, errors)
        self.assertIn({'birthdate': required_field_error}, errors)
        self.assertIn({'amount': required_field_error}, errors)
        self.assertIn({'terms': required_field_error}, errors)
        self.assertIn({'income': required_field_error}, errors)

    def test_insert_amount_out_of_limit(self):
        data = self._data_input()
        data['amount'] = '999.99'

        with self.assertRaises(LoanException) as exc:
            self.service.insert(data)

        errors = exc.exception.args[0]
        self.assertIn({'amount': 'Out of limit allowed'}, errors)

    def test_get_loans_in_process(self):
        mommy.make('Loan', status='processing', _quantity=3)
        mommy.make('Loan', status='completed', _quantity=5)

        result = self.service.get_loans_in_process()
        self.assertEqual(3, len(result))
        [self.assertEqual('processing', loan.status) for loan in result]

    def test_refuse_loan(self):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        mommy.make('Loan', id=loan_id, status='processing')

        self.service.refuse_loan(loan_id, 'age')

        result = Loan.objects.get(id=loan_id)
        self.assertEqual(result.status, 'completed')
        self.assertEqual(result.refused_policy, 'age')
        self.assertEqual(result.result, 'rejected')

    def test_approve_loan(self):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        expected_amount_approved = Decimal('5000.70')
        expected_terms_approved = 9
        mommy.make('Loan', id=loan_id, status='processing')

        self.service.approve_loan(loan_id, expected_terms_approved, expected_amount_approved)

        result = Loan.objects.get(id=loan_id)
        self.assertEqual(result.status, 'completed')
        self.assertEqual(result.result, 'approved')
        self.assertEqual(result.amount_approved, expected_amount_approved)
        self.assertEqual(result.terms_approved, expected_terms_approved)


class TestCreditService(SimpleTestCase):

    def setUp(self):
        self.service = CreditService()

    @mock.patch('credit.services.requests.post')
    def test_get_credit_score(self, mock_post):
        mock_post.return_value = mock.Mock(text=json.dumps({'score': 500}))
        expected_url = settings.SCORE_URL
        expected_token = settings.CREDIT_VALIDATION_TOKEN
        cpf = '12345678901'

        score = self.service.get_credit_score(cpf)

        self.assertEqual(score, 500)
        mock_post.assert_called_once_with(expected_url, json={"cpf": cpf}, headers={'x-api-key': expected_token})

    @mock.patch('credit.services.requests.post')
    def test_get_commitment_pct(self, mock_post):
        mock_post.return_value = mock.Mock(text=json.dumps({'commitment': '0.7'}))

        expected_url = settings.COMMITMENT_URL
        expected_token = settings.CREDIT_VALIDATION_TOKEN
        cpf = '12345678901'

        commitment = self.service.get_commitment_pct(cpf)

        self.assertEqual(commitment, Decimal('0.7'))
        mock_post.assert_called_once_with(expected_url, json={"cpf": cpf}, headers={'x-api-key': expected_token})
