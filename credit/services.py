from .models import Loan


class LoanService:

    def __init__(self):
        self.errors = []

    def insert(self, data):
        name = data.get('name')
        cpf = data.get('cpf')
        birthdate = data.get('birthdate')
        amount_asked = data.get('amount')
        terms_asked = data.get('terms')
        income = data.get('income')

        loan = Loan(
            name=name,
            cpf=cpf,
            birthdate=birthdate,
            amount_asked=amount_asked,
            terms_asked=terms_asked,
            income=income,
        )

        loan.save()

        return loan
