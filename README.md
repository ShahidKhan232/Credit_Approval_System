# Credit Approval System

A Django-based credit approval system with automated credit scoring, loan eligibility checking, and background data processing.

## Features

- **Customer Registration** with automatic credit limit calculation
- **Credit Scoring System** with 5 weighted components:
  - Payment history (35%)
  - Number of loans (25%)
  - Current year activity (20%)
  - Loan volume (15%)
  - Credit utilization (5%)
- **Loan Eligibility Checking** with dynamic interest rate correction
- **Loan Management** with EMI calculations using compound interest
- **Background Data Ingestion** from Excel files using Celery
- **RESTful API** with Django REST Framework
- **Fully Dockerized** application with PostgreSQL and Redis

## Tech Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL 15
- **Task Queue**: Celery with Redis
- **Containerization**: Docker, Docker Compose

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Installation & Setup

1. **Clone the repository** (or navigate to the project directory)

```bash
cd "Credit_Approval_System"
```

2. **Build and start all services**

```bash
docker-compose up --build
```

This will start:
- PostgreSQL database (port 5432)
- Redis (port 6379)
- Django web server (port 8000)
- Celery worker

3. **Run database migrations** (in a new terminal)

```bash
docker-compose exec web python manage.py migrate
```

4. **Create a superuser** (optional, for admin access)

```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Ingest initial data** from Excel files

```bash
docker-compose exec web python manage.py ingest_data
```

The application will be available at `http://localhost:8000`

## API Endpoints

### 1. Register Customer

**POST** `/register`

Register a new customer with automatic credit limit calculation.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": "1234567890"
}
```

**Response:**
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": "50000.00",
  "approved_limit": "1800000.00",
  "phone_number": "1234567890"
}
```

### 2. Check Loan Eligibility

**POST** `/check-eligibility`

Check if a customer is eligible for a loan based on credit score.

**Request Body:**
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.5,
  "tenure": 12
}
```

**Response:**
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.5,
  "corrected_interest_rate": 10.5,
  "tenure": 12,
  "monthly_installment": 17541.23
}
```

### 3. Create Loan

**POST** `/create-loan`

Create a new loan if eligible.

**Request Body:**
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.5,
  "tenure": 12
}
```

**Response:**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 17541.23
}
```

### 4. View Loan Details

**GET** `/view-loan/<loan_id>`

Get details of a specific loan.

**Response:**
```json
{
  "loan_id": 1,
  "customer": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "1234567890",
    "age": 30
  },
  "loan_amount": "200000.00",
  "interest_rate": "10.50",
  "monthly_installment": 17541.23,
  "tenure": 12
}
```

### 5. View Customer Loans

**GET** `/view-loans/<customer_id>`

Get all loans for a specific customer.

**Response:**
```json
[
  {
    "loan_id": 1,
    "loan_amount": "200000.00",
    "interest_rate": "10.50",
    "monthly_installment": 17541.23,
    "repayments_left": 8
  }
]
```

## Credit Scoring Logic

The system calculates credit scores (0-100) based on:

1. **Payment History (35%)**: Percentage of EMIs paid on time
2. **Loan Count (25%)**: Optimal range is 2-5 loans
3. **Current Year Activity (20%)**: 1-2 loans in current year is ideal
4. **Loan Volume (15%)**: Total loan amount vs approved limit
5. **Credit Utilization (5%)**: Current debt vs approved limit

### Approval Rules

- **Credit Score > 50**: Approve with any interest rate
- **30 < Credit Score ≤ 50**: Approve only if interest rate ≥ 12%
- **10 < Credit Score ≤ 30**: Approve only if interest rate ≥ 16%
- **Credit Score ≤ 10**: Reject loan
- **Total EMI > 50% of salary**: Reject loan
- **Current debt > approved limit**: Credit score = 0

## Project Structure

```
Backend Internship Assignment/
├── credit_system/          # Django project settings
│   ├── __init__.py
│   ├── settings.py        # Main settings
│   ├── urls.py            # URL routing
│   ├── celery.py          # Celery configuration
│   ├── wsgi.py
│   └── asgi.py
├── loans/                  # Main application
│   ├── models.py          # Customer & Loan models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── services.py        # Business logic (credit scoring)
│   ├── utils.py           # Utility functions (EMI calculation)
│   ├── tasks.py           # Celery tasks
│   ├── urls.py            # App URL routing
│   ├── admin.py           # Admin configuration
│   └── management/
│       └── commands/
│           └── ingest_data.py  # Data ingestion command
├── customer_data.xlsx      # Customer data file
├── loan_data.xlsx          # Loan data file
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── manage.py              # Django management script
```

## Development

### Running Tests

```bash
docker-compose exec web python manage.py test
```

### Accessing Django Admin

1. Create a superuser (if not already done):
```bash
docker-compose exec web python manage.py createsuperuser
```

2. Visit `http://localhost:8000/admin`

### Viewing Celery Logs

```bash
docker-compose logs -f celery
```

### Stopping Services

```bash
docker-compose down
```

### Stopping Services and Removing Volumes

```bash
docker-compose down -v
```

## Data Ingestion

The system can ingest customer and loan data from Excel files:

- `customer_data.xlsx`: Customer information
- `loan_data.xlsx`: Historical loan data

Data ingestion runs as a background task using Celery:

```bash
docker-compose exec web python manage.py ingest_data
```

## Environment Variables

Key environment variables (see `.env.example`):

- `DEBUG`: Debug mode (0 or 1)
- `SECRET_KEY`: Django secret key
- `DATABASE_NAME`: PostgreSQL database name
- `DATABASE_USER`: PostgreSQL username
- `DATABASE_PASSWORD`: PostgreSQL password
- `DATABASE_HOST`: PostgreSQL host
- `DATABASE_PORT`: PostgreSQL port
- `CELERY_BROKER_URL`: Redis URL for Celery
- `CELERY_RESULT_BACKEND`: Redis URL for results

## Testing the API

You can test the API using curl, Postman, or any HTTP client.

### Example: Register a Customer

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "age": 28,
    "monthly_income": 60000,
    "phone_number": "9876543210"
  }'
```

### Example: Check Eligibility

```bash
curl -X POST http://localhost:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 300000,
    "interest_rate": 11,
    "tenure": 24
  }'
```

## Notes

- The system uses **compound interest** for EMI calculations
- Approved credit limit = 36 × monthly_salary (rounded to nearest lakh)
- All monetary values are stored with 2 decimal precision
- Dates are stored in ISO format (YYYY-MM-DD)
- The system automatically updates customer debt when loans are created

## License

This project is created as part of a backend internship assignment.
