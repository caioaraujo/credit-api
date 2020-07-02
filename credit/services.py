from decimal import Decimal

from .exceptions import LoanException
from .models import Loan

MIN_AMOUNT_ALLOWED = Decimal('1000')
MAX_AMOUNT_ALLOWED = Decimal('4000')
REQUIRED_FIELD = 'Required field'


class LoanService:

    def __init__(self):
        self.errors = []

    def insert(self, data):
        self._validate_data(data)

        if len(self.errors):
            raise LoanException(self.errors)

        loan = Loan(
            name=data['name'],
            cpf=data['cpf'],
            birthdate=data['birthdate'],
            amount_asked=Decimal(data['amount']),
            terms_asked=data['terms'],
            income=Decimal(data['income']),
        )

        loan.save()

        return loan

    def _validate_data(self, data):
        name = data.get('name')
        if not name:
            self.errors.append({'name': REQUIRED_FIELD})
        cpf = data.get('cpf')
        if not cpf:
            self.errors.append({'cpf': REQUIRED_FIELD})
        birthdate = data.get('birthdate')
        if not birthdate:
            self.errors.append({'birthdate': REQUIRED_FIELD})
        amount_asked = data.get('amount')
        if not amount_asked:
            self.errors.append({'amount': REQUIRED_FIELD})
        elif Decimal(amount_asked) < MIN_AMOUNT_ALLOWED or MAX_AMOUNT_ALLOWED < Decimal(amount_asked):
            self.errors.append({'amount': 'Out of limit allowed'})
        terms_asked = data.get('terms')
        if not terms_asked:
            self.errors.append({'terms': REQUIRED_FIELD})
        income = data.get('income')
        if not income:
            self.errors.append({'income': REQUIRED_FIELD})
