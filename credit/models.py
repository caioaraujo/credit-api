import uuid
from django.db import models


class Loan(models.Model):

    class TermsOptions(models.IntegerChoices):
        SIX = 6
        NINE = 9
        TWELVE = 12

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    cpf = models.CharField(max_length=11)
    birthdate = models.DateField()
    amount_asked = models.DecimalField(decimal_places=2, max_digits=4)
    terms_asked = models.IntegerField(choices=TermsOptions.choices)
    income = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(max_length=10, default='processing')
    result = models.CharField(max_length=8, null=True)
    refused_policy = models.CharField(max_length=10, null=True)
    amount_approved = models.DecimalField(decimal_places=2, max_digits=4, null=True)
    terms_approved = models.IntegerField(null=True)
