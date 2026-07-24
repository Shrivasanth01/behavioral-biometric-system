# API Documentation

Base URL: `https://app.bbs-platform.com/api`

All API endpoints return JSON. Timestamps use ISO 8601 format. Monetary values use decimal strings with 2 decimal places.

## Standard Response Format

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

```json
{
  "success": false,
  "error": {
    "code": "unauthorized",
    "message": "Invalid or expired token"
  }
}
```

## Authentication

### POST /api/auth/register

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "phone": "+1234567890",
  "full_name": "John Doe",
  "password": "SecureP@ss123"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Registration successful. Please login.",
  "user_id": 42
}
```

**Errors:**
| Code | HTTP Status | Description |
|---|---|---|
| `bad_request` | 400 | Invalid email, weak password |
| `conflict` | 409 | Email already registered |

**Rate Limit:** 5 requests/minute/IP

---

### POST /api/auth/login

Authenticate user and receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "device_fingerprint": {
    "user_agent": "Mozilla/5.0 ...",
    "screen_resolution": "1920x1080",
    "timezone": "America/New_York",
    "canvas_hash": "a1b2c3d4...",
    "webgl_renderer": "ANGLE (NVIDIA)",
    "combined_hash": "sha256hash..."
  }
}
```

**Response (200) - MFA not required:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJl...",
  "expires_in": 1800,
  "token_type": "bearer",
  "user": {
    "id": 42,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "customer",
    "mfa_enabled": false
  }
}
```

**Response (200) - MFA required:**
```json
{
  "mfa_required": true,
  "mfa_method": "totp",
  "temp_token": "temp_token_for_mfa_verification",
  "access_token": "",
  "refresh_token": ""
}
```

**Errors:**
| Code | HTTP Status | Description |
|---|---|---|
| `unauthorized` | 401 | Invalid credentials |
| `bad_request` | 400 | Missing required fields |
| `account_locked` | 423 | Account locked after 5 failed attempts |

**Rate Limit:** 5 requests/minute/IP

---

### POST /api/auth/refresh

Refresh an expired access token.

**Request:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJl..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 1800,
  "token_type": "bearer"
}
```

**Errors:**
| Code | HTTP Status | Description |
|---|---|---|
| `unauthorized` | 401 | Invalid/expired refresh token |
| `bad_request` | 400 | Token already used or revoked |

**Rate Limit:** 10 requests/minute/IP

---

### POST /api/auth/logout

Invalidate current session and tokens.

**Request:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJl..."
}
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Auth:** Required
**Rate Limit:** 10 requests/minute/IP

---

### POST /api/auth/verify-otp

Verify a one-time password code.

**Request:**
```json
{
  "temp_token": "temp_token_from_login",
  "otp": "123456"
}
```

**Response (200):**
```json
{
  "verified": true,
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJl..."
}
```

**Errors:**
| Code | HTTP Status | Description |
|---|---|---|
| `bad_request` | 400 | Invalid or expired OTP |
| `too_many_requests` | 429 | Max attempts exceeded |

**Rate Limit:** 5 requests/minute/IP

---

### POST /api/auth/setup-mfa

Initiate MFA setup for the authenticated user.

**Request:**
```json
{
  "method": "totp"
}
```

**Response (200):**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "otpauth://totp/BioBank:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=BioBank",
  "backup_codes": ["1234-5678", "2345-6789", "3456-7890", "4567-8901", "5678-9012"],
  "message": "Scan the QR code with your authenticator app"
}
```

**Auth:** Required
**Rate Limit:** 3 requests/minute/IP

---

### POST /api/auth/verify-mfa

Complete MFA setup by verifying the first code.

**Request:**
```json
{
  "otp_code": "123456"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "MFA enabled successfully"
}
```

**Auth:** Required
**Rate Limit:** 5 requests/minute/IP

---

### POST /api/auth/forgot-password

Request a password reset link.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

**Rate Limit:** 3 requests/15 minutes/IP

---

### POST /api/auth/reset-password

Reset password using the token from email.

**Request:**
```json
{
  "reset_token": "reset_token_from_email",
  "new_password": "NewSecureP@ss456"
}
```

**Response (200):**
```json
{
  "message": "Password reset successful"
}
```

**Rate Limit:** 3 requests/15 minutes/IP

---

### GET /api/auth/me

Get current authenticated user's profile.

**Response (200):**
```json
{
  "id": 42,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "customer",
  "mfa_enabled": true,
  "mfa_method": "totp",
  "status": "active",
  "last_login_at": "2024-01-15T10:30:00Z",
  "last_login_ip": "203.0.113.1",
  "created_at": "2023-06-01T08:00:00Z"
}
```

**Auth:** Required

---

### PUT /api/auth/me

Update current user's profile.

**Request:**
```json
{
  "full_name": "John A. Doe",
  "phone": "+1987654321",
  "preferred_language": "es"
}
```

**Response (200):**
```json
{
  "id": 42,
  "full_name": "John A. Doe",
  "phone": "+1987654321",
  "preferred_language": "es"
}
```

**Auth:** Required

---

## Banking Endpoints

### GET /api/accounts

List all accounts for the authenticated user.

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "uuid": "a1b2c3d4-...",
      "account_number": "1000123456789001",
      "account_type": "savings",
      "currency": "USD",
      "balance": "15250.75",
      "available_balance": "15250.75",
      "status": "active",
      "opened_at": "2023-06-01T08:00:00Z"
    },
    {
      "id": 2,
      "uuid": "e5f6g7h8-...",
      "account_number": "1000123456789002",
      "account_type": "current",
      "currency": "USD",
      "balance": "45000.00",
      "available_balance": "42000.00",
      "status": "active",
      "opened_at": "2023-06-15T09:00:00Z"
    }
  ],
  "total": 2
}
```

**Auth:** Required
**Rate Limit:** 30 requests/minute/IP

---

### GET /api/accounts/{account_id}

Get details of a specific account.

**Response (200):**
```json
{
  "id": 1,
  "uuid": "a1b2c3d4-...",
  "account_number": "1000123456789001",
  "account_type": "savings",
  "currency": "USD",
  "balance": "15250.75",
  "available_balance": "15250.75",
  "status": "active",
  "opened_at": "2023-06-01T08:00:00Z",
  "transaction_count": 145,
  "last_transaction_at": "2024-01-14T16:45:00Z"
}
```

**Auth:** Required
**Rate Limit:** 30 requests/minute/IP

---

### GET /api/accounts/{account_id}/transactions

Get paginated transactions for an account.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number (1-indexed) |
| `page_size` | int | 20 | Items per page (max 100) |
| `type` | string | - | Filter by type: transfer, payment, deposit, withdrawal |
| `status` | string | - | Filter by status: completed, pending, failed |
| `from_date` | string | - | Start date (ISO 8601) |
| `to_date` | string | - | End date (ISO 8601) |

**Response (200):**
```json
{
  "items": [
    {
      "id": 1001,
      "uuid": "txn-uuid-...",
      "transaction_type": "transfer",
      "amount": "500.00",
      "fee": "5.00",
      "currency": "USD",
      "reference_number": "TXN240115164500A1B2C3D4",
      "description": "Rent payment",
      "status": "completed",
      "counterparty_name": "Jane Smith",
      "counterparty_account": "1000987654321001",
      "category": "housing",
      "is_international": false,
      "created_at": "2024-01-15T16:45:00Z",
      "processed_at": "2024-01-15T16:45:02Z"
    }
  ],
  "total": 145,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

**Auth:** Required
**Rate Limit:** 30 requests/minute/IP

---

### POST /api/transactions/transfer

Create an internal transfer between accounts.

**Request:**
```json
{
  "from_account_id": 1,
  "to_account_number": "1000123456789002",
  "amount": "250.00",
  "description": "Savings transfer",
  "category": "savings"
}
```

**Response (200):**
```json
{
  "message": "Transfer successful",
  "reference": "TXN240115164500A1B2C3D4",
  "utr_number": "UTR20240115164500X1Y2Z3",
  "status": "completed",
  "new_balance": "14750.75"
}
```

**Auth:** Required
**Rate Limit:** 10 requests/minute/IP

**Risk Assessment:** This endpoint triggers a behavioral risk evaluation. Based on the risk band:
- LOW: Executed immediately
- MEDIUM: Response includes `mfa_required: true` with `temp_token`
- HIGH: Transaction blocked with `transaction_blocked` error

---

### POST /api/transactions/external

Create an external transfer to another bank.

**Request:**
```json
{
  "from_account_id": 1,
  "to_account_number": "2000123456789001",
  "ifsc_code": "SBIN0001234",
  "bank_name": "State Bank of India",
  "to_account_name": "Jane Smith",
  "amount": "10000.00",
  "description": "Invoice payment"
}
```

**Response (200):**
```json
{
  "message": "External transfer submitted",
  "reference": "TXN240115164500A1B2C3D4",
  "utr_number": "UTR20240115164500X1Y2Z3",
  "status": "pending"
}
```

**Auth:** Required
**Rate Limit:** 5 requests/minute/IP

---

### POST /api/transactions/upi

Create a UPI transfer.

**Request:**
```json
{
  "from_account_id": 1,
  "upi_id": "johndoe@paypal",
  "amount": "1500.00",
  "description": "Dinner payment"
}
```

**Response (200):**
```json
{
  "message": "UPI transfer successful",
  "reference": "TXN240115164500A1B2C3D4",
  "utr_number": "UTR20240115164500X1Y2Z3",
  "status": "completed"
}
```

**Auth:** Required
**Rate Limit:** 10 requests/minute/IP

---

### GET /api/beneficiaries

List all beneficiaries for the user.

**Response (200):**
```json
{
  "items": [
    {
      "id": 5,
      "uuid": "ben-uuid-...",
      "beneficiary_name": "Jane Smith",
      "beneficiary_account": "2000123456789001",
      "beneficiary_bank": "State Bank of India",
      "ifsc_code": "SBIN0001234",
      "nickname": "Jane",
      "relationship": "family",
      "is_active": true,
      "max_limit": "50000.00",
      "daily_limit": "25000.00",
      "added_at": "2023-08-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Auth:** Required

---

### POST /api/beneficiaries

Add a new beneficiary.

**Request:**
```json
{
  "beneficiary_name": "Jane Smith",
  "beneficiary_account": "2000123456789001",
  "beneficiary_bank": "State Bank of India",
  "ifsc_code": "SBIN0001234",
  "nickname": "Jane",
  "relationship": "family",
  "max_limit": "50000.00",
  "daily_limit": "25000.00"
}
```

**Response (201):**
```json
{
  "id": 5,
  "beneficiary_name": "Jane Smith",
  "beneficiary_account": "2000123456789001",
  "is_active": true,
  "added_at": "2024-01-15T17:00:00Z"
}
```

**Auth:** Required

---

### PUT /api/beneficiaries/{beneficiary_id}

Update beneficiary details.

**Request:**
```json
{
  "nickname": "Jane (Updated)",
  "max_limit": "75000.00"
}
```

**Response (200):**
```json
{
  "id": 5,
  "nickname": "Jane (Updated)",
  "max_limit": "75000.00"
}
```

**Auth:** Required

---

### DELETE /api/beneficiaries/{beneficiary_id}

Remove a beneficiary.

**Response (200):**
```json
{
  "success": true,
  "message": "Beneficiary deleted"
}
```

**Auth:** Required

---

### GET /api/cards

List all cards for the user.

**Response (200):**
```json
{
  "items": [
    {
      "id": 10,
      "card_type": "debit",
      "card_network": "visa",
      "card_holder_name": "John Doe",
      "masked_card_number": "4000XXXXXXXX1234",
      "last_four_digits": "1234",
      "expiry_date": "2027-06-30",
      "status": "active",
      "is_frozen": false,
      "daily_limit": "5000.00",
      "transaction_limit": "2000.00",
      "monthly_limit": "25000.00",
      "is_international_enabled": false,
      "is_contactless_enabled": true,
      "is_ecommerce_enabled": true
    }
  ],
  "total": 1
}
```

**Auth:** Required

---

### POST /api/cards/{card_id}/freeze

Freeze a card.

**Response (200):**
```json
{
  "message": "Card frozen successfully",
  "status": "frozen"
}
```

**Auth:** Required

---

### POST /api/cards/{card_id}/unfreeze

Unfreeze a card.

**Response (200):**
```json
{
  "message": "Card unfrozen successfully",
  "status": "active"
}
```

**Auth:** Required

---

### PUT /api/cards/{card_id}/limits

Update card transaction limits.

**Request:**
```json
{
  "daily_limit": "10000.00",
  "monthly_limit": "50000.00"
}
```

**Response (200):**
```json
{
  "message": "Card limits updated",
  "status": "active"
}
```

**Auth:** Required

---

### GET /api/loans

List all loans for the user.

**Response (200):**
```json
{
  "items": [
    {
      "id": 3,
      "loan_type": "personal",
      "loan_reference": "PL20240115001",
      "principal_amount": "500000.00",
      "interest_rate": 10.5,
      "interest_type": "fixed",
      "tenure_months": 60,
      "emi_amount": "10748.06",
      "outstanding_amount": "500000.00",
      "paid_amount": "0.00",
      "status": "active",
      "disbursed_at": "2024-01-15T12:00:00Z",
      "next_emi_date": "2024-02-15"
    }
  ],
  "total": 1
}
```

**Auth:** Required

---

### POST /api/loans/apply

Submit a loan application.

**Request:**
```json
{
  "account_id": 1,
  "loan_type": "personal",
  "amount": "500000.00",
  "tenure_months": 60,
  "interest_rate": 10.5
}
```

**Response (201):**
```json
{
  "message": "Loan application submitted successfully",
  "loan_id": 3,
  "loan_reference": "PL20240115001",
  "status": "pending"
}
```

**Auth:** Required

---

### GET /api/loans/{loan_id}/emi-schedule

Get the EMI schedule for a loan.

**Response (200):**
```json
{
  "emi_schedule": [
    {
      "emi_number": 1,
      "due_date": "2024-02-15",
      "amount": "10748.06",
      "principal_component": "6481.39",
      "interest_component": "4266.67",
      "balance_after": "493518.61",
      "status": "pending"
    },
    {
      "emi_number": 2,
      "due_date": "2024-03-15",
      "amount": "10748.06",
      "principal_component": "6537.30",
      "interest_component": "4210.76",
      "balance_after": "486981.31",
      "status": "pending"
    }
  ]
}
```

**Auth:** Required

---

### POST /api/loans/calculate-emi

Calculate EMI for a given loan amount.

**Request:**
```json
{
  "amount": "500000.00",
  "annual_interest_rate": 10.5,
  "tenure_months": 60
}
```

**Response (200):**
```json
{
  "emi_amount": "10748.06",
  "total_interest": "144883.60",
  "total_payable": "644883.60",
  "monthly_rate": 0.875
}
```

**Auth:** Required

---

## Behavioral Event Endpoints

### POST /api/events

Ingest a single behavioral event.

**Request:**
```json
{
  "type": "keydown",
  "key": "a",
  "code": "KeyA",
  "location": 0,
  "repeat": false,
  "alt": false,
  "ctrl": false,
  "shift": false,
  "meta": false,
  "user_id": 42,
  "session_id": "sess_a1b2c3d4e5f6",
  "page_url": "https://app.bbs-platform.com/transfer",
  "timestamp": 1705315500000
}
```

**Response (201):**
```json
{
  "event_id": 50001
}
```

**Auth:** Optional (user_id inferred from JWT if authenticated)
**Rate Limit:** 200 requests/minute/IP

---

### POST /api/events/batch

Ingest a batch of behavioral events.

**Request:**
```json
{
  "session_id": "sess_a1b2c3d4e5f6",
  "user_id": 42,
  "events": [
    {
      "type": "keydown",
      "key": "a",
      "code": "KeyA",
      "timestamp": 1705315500000
    },
    {
      "type": "mousemove",
      "x": 500,
      "y": 300,
      "speed": 2.5,
      "timestamp": 1705315500050
    }
  ],
  "fingerprint": {
    "user_agent": "Mozilla/5.0 ...",
    "combined_hash": "sha256hash..."
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "event_ids": [50001, 50002],
  "count": 2
}
```

**Auth:** Optional
**Rate Limit:** 100 requests/minute/IP (max 500 events per batch)

---

### GET /api/events/session/{session_id}

Get all events for a specific session.

**Response (200):**
```json
[
  {
    "id": 50001,
    "type": "keydown",
    "key": "a",
    "code": "KeyA",
    "timestamp": 1705315500000,
    "page_url": "https://app.bbs-platform.com/transfer",
    "created_at": "2024-01-15T10:45:00Z"
  }
]
```

**Auth:** Required

---

### GET /api/events/profile/{user_id}

Get the behavioral profile for a user.

**Response (200):**
```json
{
  "user_id": 42,
  "profile_version": 3,
  "model_version": "v2",
  "status": "active",
  "confidence_score": 87.5,
  "total_events_analyzed": 15420,
  "total_sessions_analyzed": 47,
  "mouse_pattern": {
    "cursor_velocity_mean": { "mean": 3.2, "std": 1.1 },
    "click_frequency": { "mean": 0.05, "std": 0.02 }
  },
  "keystroke_pattern": {
    "typing_speed_mean": { "mean": 5.8, "std": 0.9 },
    "key_hold_mean": { "mean": 85.0, "std": 12.5 }
  },
  "cold_start": false,
  "drift_status": "STABLE"
}
```

**Auth:** Required (self or analyst/admin)

---

### GET /api/events/profile/{user_id}/risk-history

Get historical risk scores for a user.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `days` | int | 30 | Number of days of history (max 365) |

**Response (200):**
```json
[
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "risk_score": 12.5,
    "risk_band": "LOW",
    "session_id": "sess_a1b2c3d4",
    "transaction_type": "login"
  },
  {
    "timestamp": "2024-01-15T11:00:00Z",
    "risk_score": 45.0,
    "risk_band": "MEDIUM",
    "session_id": "sess_a1b2c3d4",
    "transaction_type": "transfer"
  }
]
```

**Auth:** Required (analyst or admin for any user, customer for self)

---

## Risk & Fraud Endpoints

### POST /api/risk/assess

Perform a risk assessment for a user session or transaction.

**Request:**
```json
{
  "user_id": 42,
  "session_id": "sess_a1b2c3d4e5f6",
  "transaction_id": 1001,
  "transaction_amount": "500.00",
  "transaction_type": "transfer",
  "device_fingerprint": "sha256hashfromsdk",
  "ip_address": "203.0.113.1",
  "user_agent": "Mozilla/5.0 ..."
}
```

**Response (200):**
```json
{
  "risk_score": 23.5,
  "risk_band": "LOW",
  "decision": "ALLOW",
  "ml_score": 18.0,
  "rules_score": 35.0,
  "heuristic_score": 10.0,
  "components": {
    "ml_weight": 0.65,
    "rules_weight": 0.25,
    "heuristic_weight": 0.10
  },
  "rule_details": [],
  "heuristic_details": [],
  "model_source": "personal_v2",
  "session_id": "sess_a1b2c3d4e5f6",
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Auth:** Required
**Rate Limit:** 30 requests/minute/IP

**Risk Bands and Decisions:**

| Risk Band | Score Range | Decision | Action |
|---|---|---|---|
| LOW | 0 - 30 | ALLOW | Transaction proceeds normally |
| MEDIUM | 31 - 70 | REQUEST_MFA | Prompt for OTP/TOTP verification |
| HIGH | 71 - 100 | BLOCK_AND_ALERT | Block transaction, trigger fraud alert |

---

### GET /api/risk/score/{session_id}

Get the risk score for a specific session.

**Response (200):**
```json
{
  "session_id": "sess_a1b2c3d4e5f6",
  "risk_score": 23.5,
  "risk_band": "LOW",
  "ml_score": 18.0,
  "rules_score": 35.0,
  "heuristic_score": 10.0,
  "model_source": "personal_v2",
  "evaluated_at": "2024-01-15T11:00:00Z"
}
```

**Auth:** Required

---

### GET /api/risk/explain/{session_id}

Get explainability details for a risk assessment.

**Response (200):**
```json
{
  "risk_score": 23.5,
  "risk_band": "LOW",
  "reasons": [
    "Behavioral pattern matches historical profile within normal range",
    "Typing speed is 5% slower than personal baseline of 5.8 cps",
    "Mouse movement pattern is consistent with past sessions"
  ],
  "feature_contributions": {
    "typing_speed_mean": 0.12,
    "cursor_velocity_mean": 0.08,
    "session_duration": 0.05,
    "key_hold_mean": 0.03
  },
  "ml_score": 18.0,
  "timestamp": "2024-01-15T11:00:00Z"
}
```

**Auth:** Required

---

### GET /api/risk/alerts

Get paginated fraud alerts.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `status` | string | - | Filter: open, investigating, resolved, false_positive, dismissed |
| `severity` | string | - | Filter: info, low, medium, high, critical |

**Response (200):**
```json
{
  "items": [
    {
      "id": 501,
      "uuid": "alert-uuid-...",
      "alert_type": "high_risk_transaction",
      "alert_severity": "high",
      "status": "open",
      "title": "High-risk transaction blocked for user johndoe@example.com",
      "description": "A transfer of $10,000.00 was blocked due to high risk score (85.4)",
      "reason_codes": ["untrusted_device", "typing_speed_anomaly", "suspicious_hours"],
      "risk_score_value": 85.4,
      "user_id": 42,
      "user_email": "johndoe@example.com",
      "user_full_name": "John Doe",
      "assigned_to": null,
      "created_at": "2024-01-15T03:15:00Z"
    }
  ],
  "total": 47,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

**Auth:** Required (analyst or admin)

---

### GET /api/risk/alerts/{alert_id}

Get details of a specific fraud alert.

**Response (200):**
```json
{
  "id": 501,
  "alert_type": "high_risk_transaction",
  "alert_severity": "high",
  "status": "open",
  "title": "High-risk transaction blocked for user johndoe@example.com",
  "description": "A transfer of $10,000.00 was blocked due to high risk score (85.4)",
  "reason_codes": ["untrusted_device", "typing_speed_anomaly", "suspicious_hours"],
  "risk_score_value": 85.4,
  "anomaly_details": {
    "typing_speed_z_score": 3.2,
    "mouse_velocity_z_score": 2.8,
    "device_match": false,
    "hour_of_day": 3
  },
  "session": {
    "id": "sess_a1b2c3d4e5f6",
    "ip_address": "198.51.100.1",
    "user_agent": "Mozilla/5.0",
    "device_fingerprint": "different_hash_than_usual",
    "event_count": 245,
    "duration_seconds": 180
  },
  "user": {
    "id": 42,
    "email": "johndoe@example.com",
    "full_name": "John Doe",
    "trusted_devices": 2,
    "profile_age_days": 180,
    "total_sessions": 47
  },
  "assigned_to": null,
  "created_at": "2024-01-15T03:15:00Z"
}
```

**Auth:** Required (analyst or admin)

---

### PUT /api/risk/alerts/{alert_id}/status

Update the status of a fraud alert.

**Request:**
```json
{
  "status": "investigating",
  "assigned_to": 5,
  "resolution_notes": "Reviewing session timeline"
}
```

**Response (200):**
```json
{
  "id": 501,
  "status": "investigating",
  "assigned_to": 5,
  "updated_at": "2024-01-15T11:30:00Z"
}
```

**Auth:** Required (analyst or admin)

---

### GET /api/risk/dashboard/summary

Get executive summary for the fraud dashboard.

**Response (200):**
```json
{
  "total_users": 1520,
  "active_sessions": 234,
  "total_alerts": 47,
  "critical_alerts": 3,
  "high_alerts": 8,
  "medium_alerts": 15,
  "low_alerts": 21,
  "avg_risk_score": 22.5,
  "blocked_transactions_today": 5,
  "mfa_prompts_today": 28,
  "model_drifted_users": 12,
  "models_in_production": 3,
  "updated_at": "2024-01-15T11:30:00Z"
}
```

**Auth:** Required (analyst or admin)

---

### GET /api/risk/dashboard/trends

Get risk score trends over time.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `days` | int | 7 | Number of days (max 90) |

**Response (200):**
```json
{
  "trends": [
    {
      "date": "2024-01-09",
      "avg_risk_score": 21.3,
      "max_risk_score": 92.1,
      "total_sessions": 312,
      "blocked_count": 2,
      "mfa_count": 15
    },
    {
      "date": "2024-01-10",
      "avg_risk_score": 19.8,
      "max_risk_score": 88.5,
      "total_sessions": 287,
      "blocked_count": 1,
      "mfa_count": 12
    }
  ]
}
```

**Auth:** Required (analyst or admin)

---

### GET /api/risk/dashboard/distribution

Get risk score distribution across all sessions.

**Response (200):**
```json
{
  "very_low": { "count": 845, "percentage": 55.6 },
  "low": { "count": 412, "percentage": 27.1 },
  "medium": { "count": 178, "percentage": 11.7 },
  "high": { "count": 65, "percentage": 4.3 },
  "critical": { "count": 20, "percentage": 1.3 },
  "total_sessions": 1520
}
```

**Auth:** Required (analyst or admin)

---

## Admin Endpoints

### GET /api/admin/users

List all users (paginated).

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `role` | string | - | Filter by role: customer, analyst, admin |
| `status` | string | - | Filter by status: active, locked, suspended |
| `search` | string | - | Search by email, name, or phone |

**Response (200):**
```json
{
  "items": [
    {
      "id": 42,
      "email": "johndoe@example.com",
      "full_name": "John Doe",
      "role": "customer",
      "status": "active",
      "mfa_enabled": true,
      "created_at": "2023-06-01T08:00:00Z",
      "last_login_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1520,
  "page": 1,
  "page_size": 20,
  "total_pages": 76
}
```

**Auth:** Required (admin)

---

### GET /api/admin/users/{user_id}

Get detailed user information.

**Response (200):**
```json
{
  "id": 42,
  "email": "johndoe@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "customer",
  "mfa_enabled": true,
  "mfa_method": "totp",
  "status": "active",
  "failed_login_attempts": 0,
  "last_login_at": "2024-01-15T10:30:00Z",
  "last_login_ip": "203.0.113.1",
  "total_accounts": 2,
  "total_cards": 1,
  "total_loans": 1,
  "total_transactions": 145,
  "total_balance": "60250.75",
  "device_count": 3,
  "trusted_device_count": 2,
  "created_at": "2023-06-01T08:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Auth:** Required (admin)

---

### PUT /api/admin/users/{user_id}/status

Update user status (lock, unlock, suspend).

**Request:**
```json
{
  "status": "active",
  "reason": "Account review completed - no suspicious activity found"
}
```

**Response (200):**
```json
{
  "id": 42,
  "status": "active",
  "updated_at": "2024-01-15T11:30:00Z"
}
```

**Auth:** Required (admin)

---

### GET /api/admin/users/{user_id}/sessions

Get recent sessions for a user.

**Response (200):**
```json
[
  {
    "session_id": "sess_a1b2c3d4e5f6",
    "ip_address": "203.0.113.1",
    "device_fingerprint": "trusted_hash",
    "is_active": false,
    "logged_in_at": "2024-01-15T10:30:00Z",
    "logged_out_at": "2024-01-15T11:15:00Z",
    "last_activity_at": "2024-01-15T11:14:30Z",
    "event_count": 1542,
    "avg_risk_score": 22.3
  }
]
```

**Auth:** Required (admin)

---

### GET /api/admin/models

List all ML models.

**Response (200):**
```json
{
  "success": true,
  "items": [
    {
      "id": 1,
      "user_id": null,
      "model_type": "global_behavioral_ensemble",
      "model_version": "global.20240115.000000",
      "is_active": true,
      "metrics": {
        "accuracy": 0.94,
        "precision": 0.92,
        "recall": 0.91,
        "f1_score": 0.93,
        "user_count": 1500,
        "session_count": 45000
      },
      "session_count": 45000,
      "training_duration": 45.2,
      "trained_at": "2024-01-15T00:00:00Z"
    }
  ],
  "total": 45
}
```

**Auth:** Required (admin)

---

### GET /api/admin/models/{model_id}

Get details of a specific model.

**Response (200):**
```json
{
  "success": true,
  "id": 1,
  "user_id": null,
  "model_type": "global_behavioral_ensemble",
  "model_version": "global.20240115.000000",
  "metrics": {
    "accuracy": 0.94,
    "precision": 0.92,
    "recall": 0.91,
    "f1_score": 0.93
  },
  "is_active": true,
  "session_count": 45000,
  "training_duration": 45.2,
  "trained_at": "2024-01-15T00:00:00Z"
}
```

**Auth:** Required (admin)

---

### POST /api/admin/models/retrain

Trigger model retraining.

**Response (200):**
```json
{
  "success": true,
  "message": "Retraining triggered for global model and 10 users"
}
```

**Auth:** Required (admin)

---

### GET /api/admin/audit-logs

Get paginated audit logs.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page (max 200) |
| `action` | string | - | Filter by action type |
| `user_id` | int | - | Filter by user ID |

**Response (200):**
```json
{
  "success": true,
  "items": [
    {
      "id": 5000,
      "user_id": 42,
      "action": "internal_transfer",
      "resource_type": "transaction",
      "resource_id": "TXN240115164500A1B2C3D4",
      "details": { "amount": "500.00" },
      "ip_address": "203.0.113.1",
      "created_at": "2024-01-15T16:45:00Z"
    }
  ],
  "total": 12500,
  "page": 1,
  "page_size": 50,
  "total_pages": 250
}
```

**Auth:** Required (admin)

---

### GET /api/admin/analytics/overview

Get system-wide analytics overview.

**Response (200):**
```json
{
  "total_users": 1520,
  "active_sessions": 234,
  "total_alerts": 47,
  "critical_alerts": 3,
  "high_alerts": 8,
  "medium_alerts": 15,
  "low_alerts": 21,
  "avg_risk_score": 22.5,
  "blocked_transactions_today": 5,
  "mfa_prompts_today": 28,
  "model_drifted_users": 12,
  "models_in_production": 3,
  "updated_at": "2024-01-15T11:30:00Z"
}
```

**Auth:** Required (admin)

---

## Common Error Codes

| HTTP Status | Code | Description |
|---|---|---|
| 400 | `bad_request` | Invalid request parameters |
| 401 | `unauthorized` | Missing or invalid authentication |
| 401 | `mfa_required` | Multi-factor authentication required |
| 403 | `forbidden` | Insufficient permissions |
| 403 | `transaction_blocked` | Transaction blocked by risk engine |
| 404 | `not_found` | Resource not found |
| 409 | `conflict` | Resource already exists |
| 422 | `validation_error` | Request body validation failed |
| 423 | `account_locked` | Account temporarily locked |
| 423 | `account_frozen` | Account is frozen |
| 429 | `rate_limit` | Rate limit exceeded |
| 500 | `internal_error` | Internal server error |

## Rate Limit Headers

All responses include rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1705315560
```

## Authentication Header

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

For endpoints requiring authentication, include the JWT access token in the `Authorization` header.
