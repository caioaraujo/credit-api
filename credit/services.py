from decimal import Decimal

from .exceptions import LoanException
from .models import Loan

REQUIRED_FIELD = "Required field"


class LoanService:

    def __init__(self):
        self.errors = []

    def _append_error(self, field, error):
        self.errors.append({field: error})

    def insert(self, data):
        name = data.get('name')
        if not name:
            self._append_error('name', REQUIRED_FIELD)
        cpf = data.get('cpf')
        if not cpf:
            self._append_error('cpf', REQUIRED_FIELD)
        birthdate = data.get('birthdate')
        if not birthdate:
            self._append_error('birthdate', REQUIRED_FIELD)
        amount_asked = data.get('amount')
        if not amount_asked:
            self._append_error('amount', REQUIRED_FIELD)
        terms_asked = data.get('terms')
        if not terms_asked:
            self._append_error('terms', REQUIRED_FIELD)
        income = data.get('income')
        if not income:
            self._append_error('income', REQUIRED_FIELD)

        if len(self.errors):
            raise LoanException(self.errors)

        loan = Loan(
            name=name,
            cpf=cpf,
            birthdate=birthdate,
            amount_asked=Decimal(amount_asked),
            terms_asked=terms_asked,
            income=Decimal(income),
        )

        loan.save()

        return loan
