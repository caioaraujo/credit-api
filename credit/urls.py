from django.urls import path

from . import views

urlpatterns = [
    path('loan/', views.LoanView.as_view(), name='loan'),
    path('loan/<uuid:loan_id>/', views.LoanStatusView.as_view(), name='loan-status'),
]
