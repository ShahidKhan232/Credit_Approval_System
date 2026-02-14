from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Customer(models.Model):
    """Customer model representing loan applicants"""
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18)])
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    approved_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    current_debt = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['customer_id']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Loan(models.Model):
    """Loan model representing customer loans"""
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='loans',
        db_column='customer_id'
    )
    loan_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    tenure = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Loan tenure in months"
    )
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    monthly_repayment = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    emis_paid_on_time = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'
        indexes = [
            models.Index(fields=['customer', 'start_date']),
            models.Index(fields=['loan_id']),
            models.Index(fields=['end_date']),
        ]
        ordering = ['-start_date']

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.full_name}"

    @property
    def is_active(self):
        """Check if loan is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def total_emis(self):
        """Total number of EMIs for the loan"""
        return self.tenure

    @property
    def emis_remaining(self):
        """Calculate remaining EMIs"""
        return max(0, self.tenure - self.emis_paid_on_time)
