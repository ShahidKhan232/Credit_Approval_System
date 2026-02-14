from django.urls import path
from .views import (
    APIRootView,
    RegisterCustomerView,
    CheckEligibilityView,
    CreateLoanView,
    ViewLoanView,
    ViewCustomerLoansView
)

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('register', RegisterCustomerView.as_view(), name='register'),
    path('check-eligibility', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>', ViewLoanView.as_view(), name='view-loan'),
    path('view-loans/<int:customer_id>', ViewCustomerLoansView.as_view(), name='view-loans'),
]
