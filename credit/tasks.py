# Celery tasks file
import json
from datetime import datetime
from decimal import Decimal

import requests
from celery import shared_task
from django.conf import settings

from .models import Loan

MIN_CREDIT_SCORE = 600
RESULT_APPROVED = 'approved'
RESULT_REJECTED = 'rejected'
STATUS_COMPLETED = 'completed'
STATUS_PROCESSING = 'processing'


@shared_task
def validate_age(loan):
    birthdate = datetime.strptime(loan['birthdate'], '%Y-%m-%d')
    current_date = datetime.now()
    years_diff = current_date.year - birthdate.year
    if (
        birthdate.month < current_date.month or
        (birthdate.month == current_date.month and birthdate.day < current_date.day)
    ):
        years_diff = years_diff - 1
    if years_diff < 18:
        refuse_loan(loan['id'], 'age')
        return loan, STATUS_COMPLETED

    return loan, STATUS_PROCESSING


@shared_task
def validate_score(s, *args):
    loan = s[0]
    current_status = s[1]

    if current_status == STATUS_COMPLETED:
        return loan, current_status

    credit_score = get_credit_score(loan['cpf'])

    if credit_score < 600:
        refuse_loan(loan['id'], 'score')
        return loan, STATUS_COMPLETED

    return loan, STATUS_PROCESSING


@shared_task
def validate_commitment(s, *args):
    loan = s[0]
    current_status = s[1]
    if current_status == STATUS_COMPLETED:
        return loan, current_status

    commitment_pct = get_commitment_pct(loan['cpf'])
    amount_asked = Decimal(loan['amount_asked'])
    commitment_amount = Decimal(amount_asked - (amount_asked * commitment_pct))
    terms_approved = get_terms_approved(commitment_amount, amount_asked, loan['income'], loan['terms_asked'])

    if terms_approved == 0:
        refuse_loan(loan['id'], 'commitment')
        return loan, STATUS_COMPLETED

    amount_approved = calculate_amount_approved(amount_asked, terms_approved)

    loan_obj = Loan.objects.get(id=loan['id'])
    loan_obj.result = RESULT_APPROVED
    loan_obj.status = STATUS_COMPLETED
    loan_obj.terms_approved = terms_approved
    loan_obj.amount_approved = amount_approved
    loan_obj.save(update_fields=['result', 'status', 'terms_approved', 'amount_approved'])


def run_credit_pipeline(loan):
    credit_pipeline = (
            validate_age.s(loan) |
            validate_score.s() |
            validate_commitment.s()
    )
    credit_pipeline.apply_async()


def get_credit_score(cpf):
    url = settings.SCORE_URL
    access_token = settings.CREDIT_VALIDATION_TOKEN
    response = requests.post(url, json={"cpf": cpf}, headers={'x-api-key': access_token})
    response_dict = json.loads(response.text)

    return response_dict["score"]


def get_commitment_pct(cpf):
    url = settings.COMMITMENT_URL
    access_token = settings.CREDIT_VALIDATION_TOKEN
    response = requests.post(url, json={"cpf": cpf}, headers={'x-api-key': access_token})
    response_dict = json.loads(response.text)

    return Decimal(response_dict["commitment"])


def get_terms_approved(commitment_amount, amount_asked, income, current_term):
    amount_per_term = Decimal(current_term / amount_asked)
    if amount_per_term > commitment_amount:
        if current_term == 6:
            get_terms_approved(commitment_amount, amount_asked, income, 9)
        elif current_term == 9:
            get_terms_approved(commitment_amount, amount_asked, income, 12)
        return 0

    return current_term


def calculate_amount_approved(amount_asked, terms_approved):
    interest_rate = calculate_interest_rate(amount_asked, terms_approved)

    return amount_asked * (
            ((1 + interest_rate) ^ terms_approved * interest_rate) / ((1 + interest_rate) ^ terms_approved - 1)
    )


def calculate_interest_rate(amount_asked, terms):
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
        return interest_rules["MORE_THAN_900"][terms]
    if Decimal('800') <= amount_asked <= Decimal('899'):
        return interest_rules['800_TO_899'][terms]
    if Decimal('700') <= amount_asked <= Decimal('799'):
        return interest_rules['700_TO_799'][terms]
    return interest_rules['600_TO_699'][terms]


def refuse_loan(loan_id, refused_policy):
    loan_obj = Loan.objects.get(id=loan_id)
    loan_obj.result = RESULT_REJECTED
    loan_obj.refused_policy = refused_policy
    loan_obj.status = STATUS_COMPLETED
    loan_obj.save(update_fields=['result', 'refused_policy', 'status'])
