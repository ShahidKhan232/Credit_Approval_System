from rest_framework import serializers
from .models import Customer, Loan
from decimal import Decimal


class CustomerRegistrationSerializer(serializers.Serializer):
    """Serializer for customer registration"""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18)
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness"""
        if Customer.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Customer with this phone number already exists")
        return value


class CustomerRegistrationResponseSerializer(serializers.ModelSerializer):
    """Serializer for customer registration response"""
    name = serializers.SerializerMethodField()
    monthly_income = serializers.DecimalField(
        source='monthly_salary', 
        max_digits=12, 
        decimal_places=2
    )
    
    class Meta:
        model = Customer
        fields = [
            'customer_id', 
            'name', 
            'age', 
            'monthly_income', 
            'approved_limit', 
            'phone_number'
        ]
    
    def get_name(self, obj):
        return obj.full_name


class LoanEligibilityRequestSerializer(serializers.Serializer):
    """Serializer for loan eligibility check request"""
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    tenure = serializers.IntegerField(min_value=1)


class LoanEligibilityResponseSerializer(serializers.Serializer):
    """Serializer for loan eligibility check response"""
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()


class LoanCreationRequestSerializer(serializers.Serializer):
    """Serializer for loan creation request"""
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    tenure = serializers.IntegerField(min_value=1)


class LoanCreationResponseSerializer(serializers.Serializer):
    """Serializer for loan creation response"""
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.FloatField()


class CustomerBasicSerializer(serializers.ModelSerializer):
    """Basic customer serializer for loan views"""
    id = serializers.IntegerField(source='customer_id')
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']


class LoanDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed loan view"""
    customer = CustomerBasicSerializer(read_only=True)
    monthly_installment = serializers.DecimalField(
        source='monthly_repayment',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Loan
        fields = [
            'loan_id',
            'customer',
            'loan_amount',
            'interest_rate',
            'monthly_installment',
            'tenure'
        ]


class LoanListSerializer(serializers.ModelSerializer):
    """Serializer for loan list view"""
    repayments_left = serializers.SerializerMethodField()
    monthly_installment = serializers.DecimalField(
        source='monthly_repayment',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Loan
        fields = [
            'loan_id',
            'loan_amount',
            'interest_rate',
            'monthly_installment',
            'repayments_left'
        ]
    
    def get_repayments_left(self, obj):
        """Get number of EMIs remaining"""
        return obj.emis_remaining
