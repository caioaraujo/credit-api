from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .exceptions import LoanException
from .serializers import LoanInsertResponseSerializer, LoanSerializer, LoanStatusSerializer
from .services import LoanService


class LoanView(GenericAPIView):

    serializer_class = LoanSerializer

    def post(self, request):
        params = request.data.copy()

        try:
            data = LoanService().insert(params)
            serialized = LoanInsertResponseSerializer(data)

            return Response(serialized.data)
        except LoanException as e:
            raise ValidationError(detail=e)


class LoanStatusView(GenericAPIView):

    def get(self, request, loan_id):
        data = LoanService().get_result(loan_id)
        serialized = LoanStatusSerializer(data)

        return Response(serialized.data)
