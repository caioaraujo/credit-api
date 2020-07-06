from unittest import mock

from django.test import TestCase
from freezegun import freeze_time
from model_mommy import mommy

from ..models import Loan
from ..tasks import validate_age, validate_score


class TestLoanTasks(TestCase):

    @freeze_time('2020-01-02')
    def test_validate_age_rejected(self):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        mommy.make('Loan', id=loan_id, status='processing')
        loan = {'id': loan_id, 'birthdate': '2002-01-01'}

        validate_age(loan)

        result = Loan.objects.get(id=loan_id)
        self.assertEqual(result.status, 'completed')
        self.assertEqual(result.refused_policy, 'age')
        self.assertEqual(result.result, 'rejected')

    @freeze_time('2020-01-01')
    def test_validate_age_approved(self):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        mommy.make('Loan', id=loan_id, status='processing')
        loan = {'id': loan_id, 'birthdate': '2002-01-01'}

        validate_age(loan)

        result = Loan.objects.get(id=loan_id)
        self.assertEqual(result.status, 'processing')
        self.assertIsNone(result.refused_policy)
        self.assertIsNone(result.result)

    @mock.patch('credit.tasks.get_credit_score', return_value=500)
    def test_validate_score_rejected(self, mock_get_credit_score):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        mommy.make('Loan', id=loan_id, status='processing')
        loan = {'id': loan_id, 'cpf': '12345678901'}

        validate_score([loan, 'processing'])

        result = Loan.objects.get(id=loan_id)
        self.assertEqual(result.status, 'completed')
        self.assertEqual(result.refused_policy, 'score')
        self.assertEqual(result.result, 'rejected')

    @mock.patch('credit.tasks.get_credit_score', return_value=600)
    def test_validate_score_approved(self, mock_get_credit_score):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        mommy.make('Loan', id=loan_id, status='processing')
        loan = {'id': loan_id, 'cpf': '12345678901'}

        validate_score([loan, 'processing'])

        result = Loan.objects.get(id=loan_id)
        self.assertEqual(result.status, 'processing')
        self.assertIsNone(result.refused_policy)
        self.assertIsNone(result.result)
