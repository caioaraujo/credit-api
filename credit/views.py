from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .exceptions import LoanException
from .serializers import CreditProcessSerializer, LoanInsertResponseSerializer, LoanSerializer, LoanStatusSerializer
from .services import LoanService
from .tasks import run_credit_pipeline


class LoanView(GenericAPIView):

    serializer_class = LoanSerializer

    def post(self, request):
        params = request.data.copy()

        try:
            with transaction.atomic():
                # Process all rules and insert into database
                data = LoanService().insert(params)

                # Send to pipline for processing
                loan = CreditProcessSerializer(data)
                run_credit_pipeline(loan.data)

            # Serialize the data
            serialized = LoanInsertResponseSerializer(data)

            return Response(serialized.data)
        except LoanException as e:
            raise ValidationError(detail=e)


class LoanStatusView(GenericAPIView):

    def get(self, request, loan_id):
        data = LoanService().get_result(loan_id)
        serialized = LoanStatusSerializer(data)

        return Response(serialized.data)
