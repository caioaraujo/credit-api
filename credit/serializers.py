from rest_framework import serializers

from .models import Loan


class LoanSerializer(serializers.ModelSerializer):

    name = serializers.CharField(required=True, help_text="Customer name", max_length=120)
    cpf = serializers.CharField(required=True, help_text="Customer CPF. Digits only", max_length=11)
    birthdate = serializers.DateField(required=True, help_text="Customer birthdate in format YYYY-MM-DD")
    amount = serializers.DecimalField(required=True, help_text="Amount asked", max_digits=6, decimal_places=2,
                                      source="amount_asked", min_value=1000, max_value=4000)
    terms = serializers.ChoiceField(required=True, help_text="Number of terms asked",
                                    source="terms_asked", choices=[6, 9, 12])
    income = serializers.DecimalField(required=True, help_text="Customer total income", max_digits=12, decimal_places=2)

    class Meta:
        model = Loan
        fields = ('name', 'cpf', 'birthdate', 'amount', 'terms', 'income')


class LoanInsertResponseSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Loan
        fields = ('id',)


class LoanStatusSerializer(serializers.ModelSerializer):

    amount = serializers.DecimalField(source='amount_approved', max_digits=6, decimal_places=2)
    terms = serializers.IntegerField(source='terms_approved')

    class Meta:
        model = Loan
        fields = ('id', 'status', 'result', 'refused_policy', 'amount', 'terms')
