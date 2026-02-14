from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import date
from decimal import Decimal

from .models import Customer, Loan
from .serializers import (
    CustomerRegistrationSerializer,
    CustomerRegistrationResponseSerializer,
    LoanEligibilityRequestSerializer,
    LoanEligibilityResponseSerializer,
    LoanCreationRequestSerializer,
    LoanCreationResponseSerializer,
    LoanDetailSerializer,
    LoanListSerializer
)
from .services import LoanEligibilityService
from .utils import round_to_nearest_lakh, calculate_emi, calculate_loan_end_date


class APIRootView(APIView):
    """
    GET /
    API root endpoint with available endpoints information
    """
    
    def get(self, request):
        return Response({
            'message': 'Credit Approval System API',
            'version': '1.0',
            'endpoints': {
                'register': {
                    'url': '/register',
                    'method': 'POST',
                    'description': 'Register a new customer'
                },
                'check_eligibility': {
                    'url': '/check-eligibility',
                    'method': 'POST',
                    'description': 'Check loan eligibility for a customer'
                },
                'create_loan': {
                    'url': '/create-loan',
                    'method': 'POST',
                    'description': 'Create a new loan'
                },
                'view_loan': {
                    'url': '/view-loan/<loan_id>',
                    'method': 'GET',
                    'description': 'View details of a specific loan'
                },
                'view_customer_loans': {
                    'url': '/view-loans/<customer_id>',
                    'method': 'GET',
                    'description': 'View all loans for a customer'
                }
            },
            'documentation': '/admin'
        }, status=status.HTTP_200_OK)


class RegisterCustomerView(APIView):
    """
    POST /register
    Register a new customer
    """
    
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        
        # Calculate approved limit: 36 * monthly_salary (rounded to nearest lakh)
        approved_limit = round_to_nearest_lakh(
            36 * data['monthly_income']
        )
        
        # Create customer
        customer = Customer.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            phone_number=data['phone_number'],
            monthly_salary=data['monthly_income'],
            approved_limit=approved_limit,
            current_debt=Decimal('0')
        )
        
        response_serializer = CustomerRegistrationResponseSerializer(customer)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class CheckEligibilityView(APIView):
    """
    POST /check-eligibility
    Check loan eligibility for a customer
    """
    
    def post(self, request):
        serializer = LoanEligibilityRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        
        # Get customer
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check eligibility
        eligibility_result = LoanEligibilityService.check_eligibility(
            customer=customer,
            loan_amount=data['loan_amount'],
            interest_rate=data['interest_rate'],
            tenure=data['tenure']
        )
        
        response_serializer = LoanEligibilityResponseSerializer(eligibility_result)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class CreateLoanView(APIView):
    """
    POST /create-loan
    Create a new loan for a customer
    """
    
    def post(self, request):
        serializer = LoanCreationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        
        # Get customer
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check eligibility
        eligibility_result = LoanEligibilityService.check_eligibility(
            customer=customer,
            loan_amount=data['loan_amount'],
            interest_rate=data['interest_rate'],
            tenure=data['tenure']
        )
        
        if not eligibility_result['approval']:
            response_data = {
                'loan_id': None,
                'customer_id': customer.customer_id,
                'loan_approved': False,
                'message': eligibility_result.get('message', 'Loan not approved'),
                'monthly_installment': 0
            }
            response_serializer = LoanCreationResponseSerializer(response_data)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
        
        # Create loan
        with transaction.atomic():
            # Use corrected interest rate
            corrected_rate = Decimal(str(eligibility_result['corrected_interest_rate']))
            monthly_emi = calculate_emi(
                data['loan_amount'],
                corrected_rate,
                data['tenure']
            )
            
            start_date = date.today()
            end_date = calculate_loan_end_date(start_date, data['tenure'])
            
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=data['loan_amount'],
                tenure=data['tenure'],
                interest_rate=corrected_rate,
                monthly_repayment=monthly_emi,
                emis_paid_on_time=0,
                start_date=start_date,
                end_date=end_date
            )
            
            # Update customer's current debt
            customer.current_debt += monthly_emi * data['tenure']
            customer.save()
        
        response_data = {
            'loan_id': loan.loan_id,
            'customer_id': customer.customer_id,
            'loan_approved': True,
            'message': 'Loan approved successfully',
            'monthly_installment': float(monthly_emi)
        }
        
        response_serializer = LoanCreationResponseSerializer(response_data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class ViewLoanView(APIView):
    """
    GET /view-loan/<loan_id>
    View details of a specific loan
    """
    
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ViewCustomerLoansView(APIView):
    """
    GET /view-loans/<customer_id>
    View all loans for a specific customer
    """
    
    def get(self, request, customer_id):
        # Verify customer exists
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Get all loans for customer
        loans = Loan.objects.filter(customer=customer)
        
        serializer = LoanListSerializer(loans, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
