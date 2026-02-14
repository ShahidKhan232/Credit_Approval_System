from django.contrib import admin
from .models import Customer, Loan


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'full_name', 'phone_number', 'monthly_salary', 'approved_limit', 'current_debt']
    search_fields = ['first_name', 'last_name', 'phone_number']
    list_filter = ['created_at']
    readonly_fields = ['customer_id', 'created_at', 'updated_at']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'tenure', 'start_date', 'end_date']
    search_fields = ['loan_id', 'customer__first_name', 'customer__last_name']
    list_filter = ['start_date', 'end_date']
    readonly_fields = ['loan_id', 'created_at', 'updated_at']
    raw_id_fields = ['customer']
