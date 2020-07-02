from unittest.mock import patch

from django.test import TestCase
from model_mommy import mommy

from ..tasks import validate_age


class TestLoanTasks(TestCase):

    @patch('credit.services.LoanService.get_loans_in_process')
    def test_validate_age(self, get_loans_in_process):
        loans = mommy.make('Loan', status='processing', _quantity=3)
        get_loans_in_process.return_value = loans

        loans = validate_age()
        self.assertEqual(3, len(loans))
