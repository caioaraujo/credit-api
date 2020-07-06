from unittest import mock

from django.test import TestCase
from freezegun import freeze_time

from ..tasks import validate_age, validate_score


class TestLoanTasks(TestCase):

    @freeze_time('2020-01-02')
    @mock.patch('credit.tasks.LoanService.refuse_loan')
    def test_validate_age_rejected(self, mock_refuse_loan):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        loan = {'id': loan_id, 'birthdate': '2002-01-01'}

        validate_age(loan)

        mock_refuse_loan.assert_called_once_with(loan_id, 'age')

    @freeze_time('2020-01-01')
    @mock.patch('credit.tasks.LoanService.refuse_loan')
    def test_validate_age_approved(self, mock_refuse_loan):
        loan = {'id': 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2', 'birthdate': '2002-01-01'}

        validate_age(loan)

        mock_refuse_loan.assert_not_called()

    @mock.patch('credit.tasks.LoanService.refuse_loan')
    @mock.patch('credit.tasks.CreditService.get_credit_score', return_value=500)
    def test_validate_score_rejected(self, mock_get_credit_score, mock_refuse_loan):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        loan = {'id': loan_id, 'cpf': '12345678901'}

        validate_score([loan, 'processing'])

        mock_get_credit_score.assert_called_once_with(loan['cpf'])
        mock_refuse_loan.assert_called_once_with(loan_id, 'score')

    @mock.patch('credit.tasks.LoanService.refuse_loan')
    @mock.patch('credit.tasks.CreditService.get_credit_score', return_value=600)
    def test_validate_score_approved(self, mock_get_credit_score, mock_refuse_loan):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        loan = {'id': loan_id, 'cpf': '12345678901'}

        validate_score([loan, 'processing'])

        mock_get_credit_score.assert_called_once_with(loan['cpf'])
        mock_refuse_loan.assert_not_called()
