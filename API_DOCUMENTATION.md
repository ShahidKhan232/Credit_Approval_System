# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Register Customer

Register a new customer in the system with automatic credit limit calculation.

**Endpoint:** `POST /register`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| first_name | string | Yes | Customer's first name |
| last_name | string | Yes | Customer's last name |
| age | integer | Yes | Customer's age (minimum 18) |
| monthly_income | decimal | Yes | Monthly income in currency units |
| phone_number | string | Yes | Unique phone number |

**Example Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": "1234567890"
}
```

**Response Body:**
| Field | Type | Description |
|-------|------|-------------|
| customer_id | integer | Unique customer ID |
| name | string | Full name of customer |
| age | integer | Customer's age |
| monthly_income | decimal | Monthly income |
| approved_limit | decimal | Approved credit limit (36 × monthly_income, rounded to nearest lakh) |
| phone_number | string | Phone number |

**Example Response (201 Created):**
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

**Error Responses:**
- `400 Bad Request`: Invalid input data or phone number already exists

---

### 2. Check Loan Eligibility

Check if a customer is eligible for a loan based on their credit score and financial status.

**Endpoint:** `POST /check-eligibility`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| customer_id | integer | Yes | Customer's unique ID |
| loan_amount | decimal | Yes | Requested loan amount |
| interest_rate | decimal | Yes | Requested annual interest rate (%) |
| tenure | integer | Yes | Loan tenure in months |

**Example Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.5,
  "tenure": 12
}
```

**Response Body:**
| Field | Type | Description |
|-------|------|-------------|
| customer_id | integer | Customer's unique ID |
| approval | boolean | Whether loan is approved |
| interest_rate | float | Requested interest rate |
| corrected_interest_rate | float | Corrected interest rate based on credit score |
| tenure | integer | Loan tenure in months |
| monthly_installment | float | Monthly EMI amount |

**Example Response (200 OK):**
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

**Eligibility Rules:**
- Credit score > 50: Approve with any interest rate
- 30 < Credit score ≤ 50: Approve only if interest rate ≥ 12%
- 10 < Credit score ≤ 30: Approve only if interest rate ≥ 16%
- Credit score ≤ 10: Reject
- Total EMI > 50% of monthly salary: Reject
- Current debt > approved limit: Credit score = 0

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Customer not found

---

### 3. Create Loan

Create a new loan for a customer if they are eligible.

**Endpoint:** `POST /create-loan`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| customer_id | integer | Yes | Customer's unique ID |
| loan_amount | decimal | Yes | Requested loan amount |
| interest_rate | decimal | Yes | Requested annual interest rate (%) |
| tenure | integer | Yes | Loan tenure in months |

**Example Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10.5,
  "tenure": 12
}
```

**Response Body:**
| Field | Type | Description |
|-------|------|-------------|
| loan_id | integer/null | Unique loan ID if approved, null otherwise |
| customer_id | integer | Customer's unique ID |
| loan_approved | boolean | Whether loan was approved |
| message | string | Approval or rejection message |
| monthly_installment | float | Monthly EMI amount |

**Example Response - Approved (201 Created):**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 17541.23
}
```

**Example Response - Rejected (200 OK):**
```json
{
  "loan_id": null,
  "customer_id": 1,
  "loan_approved": false,
  "message": "Credit score too low for loan approval",
  "monthly_installment": 0
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Customer not found

---

### 4. View Loan Details

Get detailed information about a specific loan.

**Endpoint:** `GET /view-loan/<loan_id>`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| loan_id | integer | Unique loan ID |

**Example Request:**
```
GET /view-loan/1
```

**Response Body:**
| Field | Type | Description |
|-------|------|-------------|
| loan_id | integer | Unique loan ID |
| customer | object | Customer details |
| customer.id | integer | Customer ID |
| customer.first_name | string | Customer's first name |
| customer.last_name | string | Customer's last name |
| customer.phone_number | string | Customer's phone number |
| customer.age | integer | Customer's age |
| loan_amount | decimal | Loan amount |
| interest_rate | decimal | Annual interest rate (%) |
| monthly_installment | float | Monthly EMI amount |
| tenure | integer | Loan tenure in months |

**Example Response (200 OK):**
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

**Error Responses:**
- `404 Not Found`: Loan not found

---

### 5. View Customer Loans

Get all loans for a specific customer.

**Endpoint:** `GET /view-loans/<customer_id>`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| customer_id | integer | Unique customer ID |

**Example Request:**
```
GET /view-loans/1
```

**Response Body:**
Array of loan objects, each containing:

| Field | Type | Description |
|-------|------|-------------|
| loan_id | integer | Unique loan ID |
| loan_amount | decimal | Loan amount |
| interest_rate | decimal | Annual interest rate (%) |
| monthly_installment | float | Monthly EMI amount |
| repayments_left | integer | Number of EMIs remaining |

**Example Response (200 OK):**
```json
[
  {
    "loan_id": 1,
    "loan_amount": "200000.00",
    "interest_rate": "10.50",
    "monthly_installment": 17541.23,
    "repayments_left": 8
  },
  {
    "loan_id": 2,
    "loan_amount": "150000.00",
    "interest_rate": "12.00",
    "monthly_installment": 13353.12,
    "repayments_left": 15
  }
]
```

**Error Responses:**
- `404 Not Found`: Customer not found

---

## Credit Scoring Algorithm

The system calculates credit scores (0-100) using 5 weighted components:

### Components and Weights

1. **Payment History (35%)**
   - Calculated as: (EMIs paid on time / Total EMIs) × 100
   - Higher percentage = better score

2. **Loan Count (25%)**
   - Optimal range: 2-5 loans = 100 points
   - 1 loan = 70 points
   - 6-10 loans = 80 points
   - More than 10 loans = decreasing score

3. **Current Year Activity (20%)**
   - 1-2 loans in current year = 100 points
   - 0 loans = 60 points
   - 3-4 loans = 80 points
   - More than 4 loans = 50 points

4. **Loan Volume (15%)**
   - Total loan amount vs approved limit
   - Ratio ≤ 1 = 100 points
   - Ratio ≤ 2 = 80 points
   - Ratio ≤ 3 = 60 points
   - Ratio > 3 = 40 points

5. **Credit Utilization (5%)**
   - Current debt / Approved limit
   - ≤ 30% = 100 points
   - ≤ 50% = 80 points
   - ≤ 70% = 60 points
   - ≤ 90% = 40 points
   - > 90% = 20 points

### Special Rules

- If current debt > approved limit: Credit score = 0
- New customers with no history: Credit score = 50

---

## EMI Calculation

The system uses **compound interest** formula:

```
EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)

Where:
  P = Principal loan amount
  r = Monthly interest rate (annual rate / 12 / 100)
  n = Number of monthly installments (tenure)
```

**Example:**
- Loan Amount: ₹200,000
- Annual Interest Rate: 10.5%
- Tenure: 12 months
- Monthly Interest Rate: 10.5 / 12 / 100 = 0.00875
- EMI: ₹17,541.23

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request creating a resource
- `400 Bad Request`: Invalid input data or validation errors
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a descriptive message:

```json
{
  "error": "Customer not found"
}
```

Or validation errors:

```json
{
  "field_name": [
    "Error message for this field"
  ]
}
```

---

## Testing with cURL

### Register Customer
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

### Check Eligibility
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

### Create Loan
```bash
curl -X POST http://localhost:8000/create-loan \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 300000,
    "interest_rate": 11,
    "tenure": 24
  }'
```

### View Loan
```bash
curl http://localhost:8000/view-loan/1
```

### View Customer Loans
```bash
curl http://localhost:8000/view-loans/1
```
