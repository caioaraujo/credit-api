from rest_framework import serializers

from .models import Loan


class LoanSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True, help_text="Customer name", max_length=120)
    cpf = serializers.CharField(required=True, help_text="Customer CPF. Digits only", max_length=11)
    birthdate = serializers.DateField(required=True, help_text="Customer birthdate in format YYYY-MM-DD")
    amount = serializers.DecimalField(required=True, help_text="Amount asked", max_digits=6, decimal_places=2,
                                      source="amount_asked")
    terms = serializers.IntegerField(required=True, help_text="Number of terms asked. Values allowed: 6, 9 or 12",
                                     source="terms_asked")
    income = serializers.DecimalField(required=True, help_text="Customer total income", max_digits=12, decimal_places=2)

    class Meta:
        model = Loan
        fields = ('name', 'cpf', 'birthdate', 'amount', 'terms', 'income')


class LoanInsertResponseSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Loan
        fields = ('id',)
