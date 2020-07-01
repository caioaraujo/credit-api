from django.test import TestCase

from ..models import Loan


class TestLoan(TestCase):

    def test_default_values(self):
        loan = Loan(
            name="abc",
            cpf="111111111",
            birthdate="1980-01-01",
            amount_asked="1290.90",
            terms_asked=6,
            income="5000.00",
        )

        loan.save()

        self.assertEqual(loan.status, "processing")
        self.assertIsNone(loan.amount_approved)
