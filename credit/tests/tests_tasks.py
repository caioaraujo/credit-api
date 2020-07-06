from decimal import Decimal
from unittest import mock

from django.test import SimpleTestCase
from freezegun import freeze_time

from ..tasks import validate_age, validate_commitment, validate_score


class TestLoanTasks(SimpleTestCase):

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

    @mock.patch('credit.tasks.LoanService.refuse_loan')
    @mock.patch('credit.tasks.CreditService.get_commitment_pct', return_value=Decimal('0.7'))
    @mock.patch('credit.tasks.CreditService.get_terms_approved', return_value=0)
    def test_validate_commitment_rejected(self, mock_get_terms_approved, mock_get_commitment_pct, mock_refuse_loan):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        loan = {
            'id': loan_id,
            'cpf': '12345678901',
            'amount_asked': Decimal('3245.78'),
            'income': Decimal('4500.25'),
            'terms_asked': 6
        }

        validate_commitment([loan, 'processing'])

        mock_get_terms_approved.assert_called_once_with(
            Decimal('973.734'), loan['amount_asked'], loan['income'], loan['terms_asked']
        )
        mock_get_commitment_pct.assert_called_once_with(loan['cpf'])
        mock_refuse_loan.assert_called_once_with(loan_id, 'commitment')

    @mock.patch('credit.tasks.LoanService.refuse_loan')
    @mock.patch('credit.tasks.LoanService.approve_loan')
    @mock.patch('credit.tasks.CreditService.get_commitment_pct', return_value=Decimal('0.7'))
    @mock.patch('credit.tasks.CreditService.get_terms_approved', return_value=6)
    @mock.patch('credit.tasks.CreditService.calculate_amount_approved', return_value=Decimal('7000'))
    def test_validate_commitment_approved(
        self,
        mock_calculate_amount_approved,
        mock_get_terms_approved,
        mock_get_commitment_pct,
        mock_approve_loan,
        mock_refuse_loan,
    ):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'
        loan = {
            'id': loan_id,
            'cpf': '12345678901',
            'amount_asked': Decimal('3245.78'),
            'income': Decimal('4500.25'),
            'terms_asked': 6
        }

        validate_commitment([loan, 'processing'])

        mock_get_terms_approved.assert_called_once_with(
            Decimal('973.734'), loan['amount_asked'], loan['income'], loan['terms_asked']
        )
        mock_get_commitment_pct.assert_called_once_with(loan['cpf'])
        mock_calculate_amount_approved.assert_called_once_with(loan['amount_asked'], 6)
        mock_approve_loan.assert_called_once_with(loan_id, 6, Decimal('7000'))
        mock_refuse_loan.assert_not_called()
