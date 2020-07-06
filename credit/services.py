import json
from decimal import Decimal

import requests
from django.conf import settings

from .exceptions import LoanException
from .models import Loan


class LoanService:
    MAX_AMOUNT_ALLOWED = Decimal('4000')
    MIN_AMOUNT_ALLOWED = Decimal('1000')
    REQUIRED_FIELD = 'Required field'
    RESULT_APPROVED = 'approved'
    RESULT_REJECTED = 'rejected'
    STATUS_COMPLETED = 'completed'

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

    def get_result(self, loan_id):
        return Loan.objects.get(id=loan_id)

    def get_loans_in_process(self):
        return Loan.objects.filter(status='processing')

    def refuse_loan(self, loan_id, refused_policy):
        loan_obj = Loan.objects.get(id=loan_id)
        loan_obj.result = self.RESULT_REJECTED
        loan_obj.refused_policy = refused_policy
        loan_obj.status = self.STATUS_COMPLETED
        loan_obj.save(update_fields=['result', 'refused_policy', 'status'])

    def approve_loan(self, loan_id, terms_approved, amount_approved):
        loan_obj = Loan.objects.get(id=loan_id)
        loan_obj.result = self.RESULT_APPROVED
        loan_obj.status = self.STATUS_COMPLETED
        loan_obj.terms_approved = terms_approved
        loan_obj.amount_approved = amount_approved
        loan_obj.save(update_fields=['result', 'status', 'terms_approved', 'amount_approved'])

    def _validate_data(self, data):
        name = data.get('name')
        if not name:
            self.errors.append({'name': self.REQUIRED_FIELD})
        cpf = data.get('cpf')
        if not cpf:
            self.errors.append({'cpf': self.REQUIRED_FIELD})
        birthdate = data.get('birthdate')
        if not birthdate:
            self.errors.append({'birthdate': self.REQUIRED_FIELD})
        amount_asked = data.get('amount')
        if not amount_asked:
            self.errors.append({'amount': self.REQUIRED_FIELD})
        elif Decimal(amount_asked) < self.MIN_AMOUNT_ALLOWED or self.MAX_AMOUNT_ALLOWED < Decimal(amount_asked):
            self.errors.append({'amount': 'Out of limit allowed'})
        terms_asked = data.get('terms')
        if not terms_asked:
            self.errors.append({'terms': self.REQUIRED_FIELD})
        income = data.get('income')
        if not income:
            self.errors.append({'income': self.REQUIRED_FIELD})


class CreditService:

    def get_credit_score(self, cpf):
        url = settings.SCORE_URL
        access_token = settings.CREDIT_VALIDATION_TOKEN
        response = requests.post(url, json={"cpf": cpf}, headers={'x-api-key': access_token})
        response_dict = json.loads(response.text)

        return response_dict["score"]

    def get_commitment_pct(self, cpf):
        url = settings.COMMITMENT_URL
        access_token = settings.CREDIT_VALIDATION_TOKEN
        response = requests.post(url, json={"cpf": cpf}, headers={'x-api-key': access_token})
        response_dict = json.loads(response.text)

        return Decimal(response_dict["commitment"])

    def get_terms_approved(self, commitment_amount, amount_asked, income, current_term):
        amount_per_term = Decimal(current_term / amount_asked)
        if amount_per_term > commitment_amount:
            if current_term == 6:
                self.get_terms_approved(commitment_amount, amount_asked, income, 9)
            elif current_term == 9:
                self.get_terms_approved(commitment_amount, amount_asked, income, 12)
            return 0

        return current_term

    def calculate_amount_approved(self, amount_asked, terms_approved):
        interest_rate = self._calculate_interest_rate(amount_asked, terms_approved)

        numerator = Decimal(pow(1 + interest_rate, terms_approved)) * interest_rate
        denominator = Decimal(pow(1 + interest_rate, terms_approved)) - Decimal('1')

        return amount_asked * (numerator / denominator)

    def _calculate_interest_rate(self, amount_asked, terms):
        interest_rules = {
            'MORE_THAN_900': {
                6: Decimal('3.9'),
                9: Decimal('4.2'),
                12: Decimal('4.5'),
            },
            '800_TO_899': {
                6: Decimal('4.7'),
                9: Decimal('5.0'),
                12: Decimal('5.3'),
            },
            '700_TO_799': {
                6: Decimal('5.5'),
                9: Decimal('5.8'),
                12: Decimal('6.1'),
            },
            '600_TO_699': {
                6: Decimal('6.4'),
                9: Decimal('6.6'),
                12: Decimal('6.9'),
            }
        }

        if amount_asked > Decimal('900'):
            return interest_rules['MORE_THAN_900'][terms]
        if Decimal('800') <= amount_asked <= Decimal('899'):
            return interest_rules['800_TO_899'][terms]
        if Decimal('700') <= amount_asked <= Decimal('799'):
            return interest_rules['700_TO_799'][terms]
        return interest_rules['600_TO_699'][terms]
