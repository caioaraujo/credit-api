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
