from rest_framework.generics import GenericAPIView


class LoanView(GenericAPIView):

    def post(self, request):
        pass


class LoanStatusView(GenericAPIView):

    def get(self, request, loan_id):
        pass
