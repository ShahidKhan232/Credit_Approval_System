from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta


def calculate_emi(principal, annual_interest_rate, tenure_months):
    """
    Calculate monthly EMI using compound interest formula
    
    Formula: EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
    where:
        P = Principal loan amount
        r = Monthly interest rate (annual rate / 12 / 100)
        n = Number of monthly installments
    
    Args:
        principal: Loan amount
        annual_interest_rate: Annual interest rate in percentage
        tenure_months: Loan tenure in months
    
    Returns:
        Monthly EMI amount (Decimal)
    """
    principal = Decimal(str(principal))
    annual_interest_rate = Decimal(str(annual_interest_rate))
    tenure_months = int(tenure_months)
    
    # Handle zero interest rate case
    if annual_interest_rate == 0:
        return principal / tenure_months
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_interest_rate / Decimal('12') / Decimal('100')
    
    # Calculate EMI using compound interest formula
    numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
    denominator = ((1 + monthly_rate) ** tenure_months) - 1
    
    emi = numerator / denominator
    
    # Round to 2 decimal places
    return round(emi, 2)


def round_to_nearest_lakh(amount):
    """
    Round amount to nearest lakh (100,000)
    
    Args:
        amount: Amount to round
    
    Returns:
        Amount rounded to nearest lakh
    """
    amount = Decimal(str(amount))
    lakh = Decimal('100000')
    return round(amount / lakh) * lakh


def calculate_loan_end_date(start_date, tenure_months):
    """
    Calculate loan end date based on start date and tenure
    
    Args:
        start_date: Loan start date
        tenure_months: Loan tenure in months
    
    Returns:
        Loan end date
    """
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    
    return start_date + relativedelta(months=tenure_months)


def get_corrected_interest_rate(credit_score, requested_rate):
    """
    Get corrected interest rate based on credit score
    
    Args:
        credit_score: Customer's credit score (0-100)
        requested_rate: Requested interest rate
    
    Returns:
        Tuple of (corrected_rate, should_approve)
    """
    requested_rate = Decimal(str(requested_rate))
    
    if credit_score > 50:
        # Approve with any rate
        return requested_rate, True
    elif 30 < credit_score <= 50:
        # Approve only if rate > 12%
        if requested_rate >= 12:
            return requested_rate, True
        else:
            return Decimal('12.00'), True
    elif 10 < credit_score <= 30:
        # Approve only if rate > 16%
        if requested_rate >= 16:
            return requested_rate, True
        else:
            return Decimal('16.00'), True
    else:
        # Don't approve
        return requested_rate, False
