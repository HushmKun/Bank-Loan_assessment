### README.md

# Bank Loan Management System

A Django-based application to manage bank loans, allowing loan providers, customers, and bank personnel to interact within specified financial constraints.

## Features

### Implemented
- **User Groups & Authentication**:
  - Provider: Submit fund applications, view their status.
  - Borrower: Apply for loans, view application status, make payments.
  - Bank Personnel: Approve/reject loan and fund applications, set loan terms (interest rate).
- **Loan Management**:
  - Total loans cannot exceed available funds.
  - Track loan payments and outstanding balances.
  - Advanced payment scheduling and interest calculations.
- **Django Admin Interface**:
  - Manage users, applications, loans, and payments.
- **REST API** (DRF):
  - Secure endpoints for each user role.
  - Authentication via JWT.

### Pending
- Frontend UI (Vuetify/React) – currently uses Django admin.

## Setup

### Prerequisites
- Python 3.8+ 
- PostgreSQL (recommended) or SQLite

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/HushmKun/bank-loan-system.git
   cd bank-loan-system
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate    # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Fill DB with mock data:
   ```bash
   python manage.py data
   ```
6. Start the server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- **All Groups**: 
  - `/api/v1/login/` (POST)         Logins user, returns access and refresh tokens.
  - `/api/v1/refresh/` (POST)       Refreshs user access token.
- **Providers**: 
    - `/api/v1/applications/` (GET) Lists all user requests 
    - `/api/v1/applications/` (POST) Creats a new deposit application 
    - `/api/v1/applications/:id/` (GET) Gets a single application where pk=id else return 404 
- **Borrowers**: 
    - `/api/v1/applications/` (GET) Lists all user requests 
    - `/api/v1/applications/` (POST) Creats a new Loan application 
    - `/api/v1/applications/:id/` (GET) Gets a single application where pk=id else return 404 
    - `/api/v1/payments/` (GET) Lists all user payments
    - `/api/v1/payments/:id/` (GET) Gets a single payment where pk=id
    - `/api/v1/payments/:id/` (PATCH) Modifies single payment to paid or failed.



## Testing
Run unit tests:
```bash
python manage.py test
```

## Usage
1. Access the admin at `http://localhost:8000/admin`.
2. Use the superuser account to:
   - Assign user roles (via Groups: "Provider", "Borrower", "Bank Personnel").
3. Loan Providers/Customers can log in via the Django admin or API to submit/view applications.


### Assumptions Document

**1. User Roles & Permissions**
- Assumed roles are managed via Django’s built-in `Groups`. Users are assigned to one group (Provider, Borrower, Bank Personnel) during registration.
- The users can only be registered by the `Bank Personnel` members.

**2. Loan Fund Applications**
- Providers submit fund applications with an amount. Once reviewed by Bank Personnel and added the interest rate, the bank’s total available funds increase by this amount.

**3. Loan Applications**
- Loan Customers apply for loans with a requested amount and term. The system checks if the loan amount ≤ (total funds - total active loans).

**4. Loan Approval**
- Bank Personnel manually Sets interest rate & approve/reject applications. Approved loans deduct from available funds.

**5. Payments**
- Payments reduce the outstanding loan balance. Assumed to be **simple interest**:  
  `Interest = Principal × Rate × Term`.  
  Payments are tracked but not automatically scheduled.

**6. Application Statuses**
- Applications have states: `Pending`, `Approved`, `Rejected`.

**7. Financial Constraints**
- Total active loans are calculated as the sum of all approved loans not yet fully repaid. The system blocks loan approvals if they exceed available funds.

**8. Security**
- API endpoints use Django’s Simple-JWT authentication. Sensitive operations (e.g., approving loans) are restricted to Bank Personnel via Django admin permissions.

**9. Interest Calculation**
- Assumed simple interest for transparency. For example, a $1000 loan at 5% interest over *any* amount of time would total $1050.

**10. Unspecified Details**
- Loan terms (e.g., duration unit) are assumed to be in months.
- No penalty for early repayment.
