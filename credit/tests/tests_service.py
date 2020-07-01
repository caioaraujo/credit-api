from django.test import TestCase

from ..models import Loan
from ..services import LoanService


class TestLoanService(TestCase):

    def test_post(self):
        service = LoanService()
        data = {
            "name": "Test",
            "cpf": "11122233309",
            "birthdate": "1980-01-01",
            "amount": "1290.90",
            "terms": 6,
            "income": "5000.00",
        }

        result = service.insert(data)

        self.assertIsInstance(result, Loan)
        self.assertIsNotNone(result.id)
