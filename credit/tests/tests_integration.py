from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase


class TestLoanView(APITestCase):

    def test_post_success(self):
        data = {
            "name": "Test",
            "cpf": "11122233309",
            "birthdate": "1980-01-01",
            "amount": "1290.90",
            "terms": 6,
            "income": "5000.00",
        }

        response = self.client.post('/v1/loan/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["id"])

    def test_post_bad_request(self):
        response = self.client.post('/v1/loan/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestLoanStatusView(APITestCase):

    def test_get_loan_in_processing_status(self):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'

        mommy.make(
            'Loan',
            id=loan_id,
            status='processing',
            result=None,
            refused_policy=None,
            amount_approved=None,
            terms_approved=None,
        )

        response = self.client.get(f'/v1/loan/{loan_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data
        self.assertEqual(result['status'], 'processing')
        self.assertIsNone(result['result'])
        self.assertIsNone(result['refused_policy'])
        self.assertIsNone(result['amount'])
        self.assertIsNone(result['terms'])

    def test_get_refused_loan(self):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'

        mommy.make(
            'Loan',
            id=loan_id,
            status='completed',
            result='refused',
            refused_policy='score',
            amount_approved=None,
            terms_approved=None,
        )

        response = self.client.get(f'/v1/loan/{loan_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['result'], 'refused')
        self.assertEqual(result['refused_policy'], 'score')
        self.assertIsNone(result['amount'])
        self.assertIsNone(result['terms'])

    def test_get_approved_loan(self):
        loan_id = 'e18c4ddf-aa3d-44e0-bccd-1030c66757e2'

        mommy.make(
            'Loan',
            id=loan_id,
            status='completed',
            result='approved',
            refused_policy=None,
            amount_approved='1560.50',
            terms_approved=9,
        )

        response = self.client.get(f'/v1/loan/{loan_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['result'], 'approved')
        self.assertIsNone(result['refused_policy'])
        self.assertEqual(result['amount'], '1560.50')
        self.assertEqual(result['terms'], 9)
