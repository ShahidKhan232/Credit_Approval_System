from decimal import Decimal
from datetime import datetime, date
from django.db.models import Sum, Count, Q
from .models import Customer, Loan
from .utils import calculate_emi, get_corrected_interest_rate


class CreditScoringService:
    """Service for calculating customer credit scores"""
    
    # Credit score component weights (total = 100)
    WEIGHT_PAYMENT_HISTORY = 35  # Past loans paid on time
    WEIGHT_LOAN_COUNT = 25       # Number of loans taken
    WEIGHT_CURRENT_YEAR = 20     # Loan activity in current year
    WEIGHT_LOAN_VOLUME = 15      # Loan approved volume
    WEIGHT_UTILIZATION = 5       # Credit utilization
    
    @staticmethod
    def calculate_credit_score(customer):
        """
        Calculate credit score for a customer (0-100)
        
        Components:
        1. Past Loans paid on time (35%)
        2. Number of loans taken in past (25%)
        3. Loan activity in current year (20%)
        4. Loan approved volume (15%)
        5. Credit utilization (5%)
        
        Args:
            customer: Customer instance
        
        Returns:
            Credit score (0-100)
        """
        # Check if current debt exceeds approved limit
        if customer.current_debt > customer.approved_limit:
            return 0
        
        loans = Loan.objects.filter(customer=customer)
        
        if not loans.exists():
            # New customer with no history - give moderate score
            return 50
        
        # Component 1: Payment history (35%)
        payment_score = CreditScoringService._calculate_payment_history_score(loans)
        
        # Component 2: Number of loans (25%)
        loan_count_score = CreditScoringService._calculate_loan_count_score(loans)
        
        # Component 3: Current year activity (20%)
        current_year_score = CreditScoringService._calculate_current_year_score(loans)
        
        # Component 4: Loan volume (15%)
        volume_score = CreditScoringService._calculate_volume_score(loans, customer)
        
        # Component 5: Credit utilization (5%)
        utilization_score = CreditScoringService._calculate_utilization_score(customer)
        
        # Calculate weighted total
        total_score = (
            payment_score * CreditScoringService.WEIGHT_PAYMENT_HISTORY / 100 +
            loan_count_score * CreditScoringService.WEIGHT_LOAN_COUNT / 100 +
            current_year_score * CreditScoringService.WEIGHT_CURRENT_YEAR / 100 +
            volume_score * CreditScoringService.WEIGHT_LOAN_VOLUME / 100 +
            utilization_score * CreditScoringService.WEIGHT_UTILIZATION / 100
        )
        
        return round(total_score, 2)
    
    @staticmethod
    def _calculate_payment_history_score(loans):
        """Calculate score based on EMIs paid on time"""
        total_emis = 0
        paid_on_time = 0
        
        for loan in loans:
            total_emis += loan.total_emis
            paid_on_time += loan.emis_paid_on_time
        
        if total_emis == 0:
            return 50  # No history
        
        payment_ratio = paid_on_time / total_emis
        return min(100, payment_ratio * 100)
    
    @staticmethod
    def _calculate_loan_count_score(loans):
        """Calculate score based on number of loans"""
        count = loans.count()
        
        # Optimal range: 2-5 loans
        if count == 0:
            return 50
        elif 2 <= count <= 5:
            return 100
        elif count == 1:
            return 70
        elif 6 <= count <= 10:
            return 80
        else:
            # Too many loans might indicate risk
            return max(30, 100 - (count - 10) * 5)
    
    @staticmethod
    def _calculate_current_year_score(loans):
        """Calculate score based on current year loan activity"""
        current_year = datetime.now().year
        current_year_loans = loans.filter(start_date__year=current_year)
        
        count = current_year_loans.count()
        
        # Moderate activity is good
        if count == 0:
            return 60  # No recent activity
        elif 1 <= count <= 2:
            return 100  # Good activity
        elif 3 <= count <= 4:
            return 80   # Moderate
        else:
            return 50   # Too much activity might indicate desperation
    
    @staticmethod
    def _calculate_volume_score(loans, customer):
        """Calculate score based on loan volume vs approved limit"""
        total_loan_amount = loans.aggregate(
            total=Sum('loan_amount')
        )['total'] or Decimal('0')
        
        if customer.approved_limit == 0:
            return 50
        
        volume_ratio = total_loan_amount / customer.approved_limit
        
        # Good if total loans are reasonable compared to limit
        if volume_ratio <= 1:
            return 100
        elif volume_ratio <= 2:
            return 80
        elif volume_ratio <= 3:
            return 60
        else:
            return 40
    
    @staticmethod
    def _calculate_utilization_score(customer):
        """Calculate score based on current debt utilization"""
        if customer.approved_limit == 0:
            return 50
        
        utilization = customer.current_debt / customer.approved_limit
        
        # Lower utilization is better
        if utilization <= 0.3:
            return 100
        elif utilization <= 0.5:
            return 80
        elif utilization <= 0.7:
            return 60
        elif utilization <= 0.9:
            return 40
        else:
            return 20


class LoanEligibilityService:
    """Service for checking loan eligibility"""
    
    @staticmethod
    def check_eligibility(customer, loan_amount, interest_rate, tenure):
        """
        Check if customer is eligible for a loan
        
        Args:
            customer: Customer instance
            loan_amount: Requested loan amount
            interest_rate: Requested interest rate
            tenure: Loan tenure in months
        
        Returns:
            Dictionary with eligibility details
        """
        # Calculate credit score
        credit_score = CreditScoringService.calculate_credit_score(customer)
        
        # Get corrected interest rate based on credit score
        corrected_rate, rate_approved = get_corrected_interest_rate(
            credit_score, 
            interest_rate
        )
        
        # Check if credit score allows approval
        if not rate_approved:
            return {
                'customer_id': customer.customer_id,
                'approval': False,
                'interest_rate': float(interest_rate),
                'corrected_interest_rate': float(corrected_rate),
                'tenure': tenure,
                'monthly_installment': 0,
                'message': 'Credit score too low for loan approval'
            }
        
        # Calculate EMI with corrected rate
        monthly_emi = calculate_emi(loan_amount, corrected_rate, tenure)
        
        # Check if sum of all current EMIs > 50% of monthly salary
        active_loans = Loan.objects.filter(
            customer=customer,
            end_date__gte=date.today()
        )
        
        current_emi_sum = sum(
            loan.monthly_repayment for loan in active_loans
        )
        
        total_emi = current_emi_sum + monthly_emi
        max_allowed_emi = customer.monthly_salary * Decimal('0.5')
        
        if total_emi > max_allowed_emi:
            return {
                'customer_id': customer.customer_id,
                'approval': False,
                'interest_rate': float(interest_rate),
                'corrected_interest_rate': float(corrected_rate),
                'tenure': tenure,
                'monthly_installment': float(monthly_emi),
                'message': 'Total EMI exceeds 50% of monthly salary'
            }
        
        # Loan approved
        return {
            'customer_id': customer.customer_id,
            'approval': True,
            'interest_rate': float(interest_rate),
            'corrected_interest_rate': float(corrected_rate),
            'tenure': tenure,
            'monthly_installment': float(monthly_emi),
            'message': 'Loan approved'
        }
