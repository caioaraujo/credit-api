from django.test import TestCase
from model_mommy import mommy

from ..tasks import validate_age


class TestLoanTasks(TestCase):

    def test_validate_age(self):
        loans = mommy.make('Loan', status='processing', _quantity=3)

        validate_age(loans)
