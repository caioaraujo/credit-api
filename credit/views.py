from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import LoanInsertResponseSerializer, LoanSerializer
from .services import LoanService


class LoanView(GenericAPIView):

    serializer_class = LoanSerializer

    def post(self, request):
        params = request.data.copy()
        data = LoanService().insert(params)
        serialized = LoanInsertResponseSerializer(data)

        return Response(serialized.data)


class LoanStatusView(GenericAPIView):

    def get(self, request, loan_id):
        pass
