# Celery tasks file
from datetime import datetime
from decimal import Decimal

from celery import shared_task

from .services import CreditService, LoanService

DATE_MASK = '%Y-%m-%d'
STATUS_COMPLETED = 'completed'
STATUS_PROCESSING = 'processing'


@shared_task
def validate_age(loan):
    birthdate = datetime.strptime(loan['birthdate'], DATE_MASK)
    current_date = datetime.now()
    years_diff = current_date.year - birthdate.year
    if (
        birthdate.month < current_date.month or
        (birthdate.month == current_date.month and birthdate.day < current_date.day)
    ):
        years_diff = years_diff - 1
    if years_diff < 18:
        LoanService().refuse_loan(loan['id'], 'age')
        return loan, STATUS_COMPLETED

    return loan, STATUS_PROCESSING


@shared_task
def validate_score(s, *args):
    loan = s[0]
    current_status = s[1]

    if current_status == STATUS_COMPLETED:
        return loan, current_status

    credit_service = CreditService()
    credit_score = credit_service.get_credit_score(loan['cpf'])

    if credit_score < 600:
        LoanService().refuse_loan(loan['id'], 'score')
        return loan, STATUS_COMPLETED

    return loan, STATUS_PROCESSING


@shared_task
def validate_commitment(s, *args):
    loan = s[0]
    current_status = s[1]
    if current_status == STATUS_COMPLETED:
        return loan, current_status

    credit_service = CreditService()
    commitment_pct = credit_service.get_commitment_pct(loan['cpf'])
    amount_asked = Decimal(loan['amount_asked'])
    commitment_amount = Decimal(amount_asked - (amount_asked * commitment_pct))
    terms_approved = credit_service.get_terms_approved(commitment_amount, amount_asked, loan['income'],
                                                       loan['terms_asked'])
    loan_service = LoanService()

    if terms_approved == 0:
        loan_service.refuse_loan(loan['id'], 'commitment')
        return loan, STATUS_COMPLETED

    amount_approved = credit_service.calculate_amount_approved(amount_asked, terms_approved)

    loan_service.approved_loan(loan['id'], terms_approved, amount_approved)


def run_credit_pipeline(loan):
    credit_pipeline = (
            validate_age.s(loan) |
            validate_score.s() |
            validate_commitment.s()
    )
    credit_pipeline.apply_async()
