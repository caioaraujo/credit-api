from rest_framework import serializers

from .models import Loan


class LoanInsertResponseSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Loan
        fields = ('id',)
