from django.test import SimpleTestCase, TestCase

from ..exceptions import LoanException
from ..models import Loan
from ..services import LoanService


class TestLoanService(TestCase):

    def test_insert_success(self):
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

    def test_insert_required_fields(self):
        required_field_error = "Required field"
        service = LoanService()

        with self.assertRaises(LoanException) as exc:
            service.insert({})

        errors = exc.exception.args[0]
        self.assertIn({"name": required_field_error}, errors)
        self.assertIn({"cpf": required_field_error}, errors)
        self.assertIn({"birthdate": required_field_error}, errors)
        self.assertIn({"amount": required_field_error}, errors)
        self.assertIn({"terms": required_field_error}, errors)
        self.assertIn({"income": required_field_error}, errors)
