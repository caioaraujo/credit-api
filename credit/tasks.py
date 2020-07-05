# Celery tasks file
from celery import shared_task


@shared_task
def validate_age(loan):
    print(loan)



@shared_task
def validate_score(loan):
    print(loan)


@shared_task
def validate_commitment(loan):
    print(loan)


def run_credit_pipeline(loan):
    credit_pipeline = (validate_age.s(loan) | validate_score.s(loan) | validate_commitment.s(loan))
    credit_pipeline.apply_async()
