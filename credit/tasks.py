# Celery tasks file
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from .services import LoanService


@shared_task
def validate_age():
    loans_in_process = LoanService().get_loans_in_process()
    return loans_in_process


# @shared_task
# def validate_score():
#     pass
#
#
# @shared_task
# def validate_commitment():
#     pass
