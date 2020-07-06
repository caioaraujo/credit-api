# Celery tasks file
from datetime import datetime

from celery import shared_task

from .models import Loan

RESULT_APPROVED = 'approved'
RESULT_REJECTED = 'rejected'
STATUS_COMPLETED = 'completed'
STATUS_PROCESSING = 'processing'


@shared_task
def validate_age(loan):
    birthdate = datetime.strptime(loan['birthdate'], '%Y-%m-%d')
    current_date = datetime.now()
    years_diff = current_date.year - birthdate.year
    if birthdate.month > current_date.month:
        years_diff = years_diff - 1
    if years_diff < 18:
        loan_obj = Loan.objects.get(id=loan['id'])
        loan_obj.result = RESULT_REJECTED
        loan_obj.refused_policy = 'age'
        loan_obj.status = STATUS_COMPLETED
        loan_obj.save(update_fields=['result', 'refused_policy', 'status'])
        return loan, STATUS_COMPLETED

    return loan, STATUS_PROCESSING


@shared_task
def validate_score(loan, current_status):
    if current_status == STATUS_COMPLETED:
        return loan, current_status
    return loan, STATUS_PROCESSING


@shared_task
def validate_commitment(loan, current_status):
    if current_status == STATUS_COMPLETED:
        return loan, current_status
    print(loan)


def run_credit_pipeline(loan):
    credit_pipeline = (
            validate_age.s(loan) | validate_score.s(STATUS_PROCESSING) | validate_commitment.s(STATUS_PROCESSING)
    )
    credit_pipeline.apply_async()
