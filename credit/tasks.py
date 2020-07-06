# Celery tasks file
import json
from datetime import datetime

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
        reject_loan(loan['id'], 'age')
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
        reject_loan(loan['id'], 'score')
        return loan, STATUS_COMPLETED

    return loan, STATUS_PROCESSING


@shared_task
def validate_commitment(s, *args):
    loan = s[0]
    current_status = s[1]
    if current_status == STATUS_COMPLETED:
        return loan, current_status
    print(loan)


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


def reject_loan(loan_id, refused_policy):
    loan_obj = Loan.objects.get(id=loan_id)
    loan_obj.result = RESULT_REJECTED
    loan_obj.refused_policy = refused_policy
    loan_obj.status = STATUS_COMPLETED
    loan_obj.save(update_fields=['result', 'refused_policy', 'status'])
