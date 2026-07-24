# User Guide

## Customer Guide

### Getting Started

#### Registration

1. Navigate to `https://app.bbs-platform.com`
2. Click **Create Account**
3. Fill in the registration form:

| Field | Description | Requirements |
|---|---|---|
| Full Name | Your legal name | 2-100 characters |
| Email Address | Your email | Valid email format |
| Phone Number | Mobile number | +CountryCode followed by number |
| Password | Account password | Min 8 chars, upper, lower, digit, special char |
| Confirm Password | Re-enter password | Must match |

4. Accept Terms of Service and Privacy Policy
5. Click **Register**
6. Check your email and verify your account (verification link expires in 24 hours)

#### Login

1. Navigate to `https://app.bbs-platform.com`
2. Enter your email and password
3. Click **Sign In**
4. If MFA is enabled, enter your authentication code

**First-time login:** Your device will be registered automatically via browser fingerprinting. This creates a baseline behavioral profile that improves security over time.

#### MFA Setup

Enabling multi-factor authentication adds an extra layer of security:

1. Go to **Settings > Security > Multi-Factor Authentication**
2. Click **Setup MFA**
3. Choose your preferred method:
   - **Authenticator App (Recommended)**: Scan the QR code with Google Authenticator, Microsoft Authenticator, or Authy
   - **SMS**: Receive codes via text message (carrier charges may apply)
   - **Email**: Receive codes via email
4. Enter the verification code from your chosen method
5. Save your backup codes in a secure location (each code can be used once)

```
┌─────────────────────────────────────┐
│  Backup Codes                       │
│                                     │
│  1. 1234-5678    4. 4567-8901      │
│  2. 2345-6789    5. 5678-9012      │
│  3. 3456-7890                       │
│                                     │
│  Store these in a safe place!       │
│  Each code can be used only once.   │
└─────────────────────────────────────┘
```

#### Device Registration

When you log in from a new device:
1. Enter your credentials normally
2. If MFA is enabled, complete the MFA challenge
3. The device is automatically registered via behavioral fingerprinting
4. You will receive a notification email about the new device login
5. You can view and manage trusted devices in **Settings > Security > Devices**

**Trust Score:** Each device accumulates a trust score based on how often you use it and how consistent your behavior is. Trusted devices may skip MFA challenges for low-risk actions.

### Banking Features

#### Viewing Accounts

The dashboard displays all your accounts:

```
┌─────────────────────────────────────────────────────────────┐
│  My Accounts                               + New Account    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Savings Account                                   │    │
│  │  ****9001                                           │    │
│  │  $15,250.75                                         │    │
│  │  Available: $15,250.75                              │    │
│  │  [View Details] [Transfer] [Transactions]           │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Current Account                                    │    │
│  │  ****9002                                           │    │
│  │  $45,000.00                                         │    │
│  │  Available: $42,000.00  (On hold: $3,000.00)       │    │
│  │  [View Details] [Transfer] [Transactions]           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

Each account card shows:
- Account type and masked number
- Current balance and available balance
- Quick action buttons

#### Making Transfers

The platform supports three types of transfers:

**1. Internal Transfer (Between your own accounts):**
1. Click **Transfer** on any account card
2. Select **Internal Transfer**
3. Choose the source account (pre-filled)
4. Enter the destination account number
5. Enter the amount
6. Add an optional description and category
7. Review the transfer details
8. If prompted, complete the behavioral verification (see below)
9. Confirm the transfer

**2. External Transfer (To another bank):**
1. Click **Transfer > External Transfer**
2. Select source account
3. Enter beneficiary details: account number, IFSC code, bank name, beneficiary name
4. Enter amount and description
5. Review and confirm
6. Complete behavioral verification if prompted

**3. UPI Transfer:**
1. Click **Transfer > UPI Transfer**
2. Select source account
3. Enter the UPI ID (e.g., `username@bank`)
4. Enter amount and description
5. Review and confirm

**Behavioral Verification:** For medium-risk transactions, the system will prompt you to complete a brief behavioral verification:

```
┌─────────────────────────────────────────────────────┐
│  🔒 Security Verification                           │
│                                                     │
│  Please complete this quick check to verify your    │
│  identity:                                          │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │  Trust Score: 45                             │    │
│  │  ████████████████░░░░░░░░░░░░░░░░░░░░░ 45%  │    │
│  │                                             │    │
│  │  Please type the following sentence:        │    │
│  │                                             │    │
│  │  "I authorize this transfer of $500.00"     │    │
│  │  ┌───────────────────────────────────────┐  │    │
│  │  │                                       │  │    │
│  │  └───────────────────────────────────────┘  │    │
│  │                                             │    │
│  │  The system is analyzing your typing         │    │
│  │  pattern to verify your identity...          │    │
│  │                                             │    │
│  │  [Cancel]                    [Verify & Send] │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

#### Managing Beneficiaries

Save beneficiaries for quick and easy transfers:

1. Go to **Beneficiaries**
2. Click **Add Beneficiary**
3. Fill in details:

| Field | Description |
|---|---|
| Beneficiary Name | Name of the person/entity |
| Account Number | Beneficiary's bank account number |
| Bank Name | Name of beneficiary's bank |
| IFSC Code | Indian Financial System Code (for domestic transfers) |
| SWIFT Code | For international transfers |
| Nickname | A friendly name for your reference |
| Relationship | Family, friend, business, etc. |
| Max Limit | Maximum amount per transaction |
| Daily Limit | Maximum amount per day |

4. Click **Save Beneficiary**

You can edit, delete, or transfer to any beneficiary from the list.

#### Paying Bills

1. Click **Payments > Bill Pay**
2. Select a biller from the list or search by name
3. Enter the amount and payment date
4. Select the source account
5. Review and confirm

**Supported bill categories:**
- Utilities (electricity, water, gas)
- Telecommunications (mobile, broadband)
- Insurance premiums
- Credit card bills
- Loan EMIs
- Taxes
- Subscription services

#### Managing Cards

View and manage your debit and credit cards:

```
┌────────────────────────────────────────────────────┐
│  My Cards                                          │
├────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────┐   │
│  │  💳 Visa Debit                              │   │
│  │  4000 XXXX XXXX 1234                        │   │
│  │  Expires: 06/27                             │   │
│  │  Status: ✅ Active                          │   │
│  │                                             │   │
│  │  Daily Limit: $5,000.00   Used: $1,200.00  │   │
│  │  Monthly Limit: $25,000.00 Used: $8,500.00 │   │
│  │                                             │   │
│  │  [Freeze] [Edit Limits] [View Transactions] │   │
│  └────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

**Freezing a card:**
1. Select the card
2. Click **Freeze Card**
3. Confirm the action
4. The card is immediately frozen - no new transactions will be accepted
5. To unfreeze, select the card and click **Unfreeze**

**Setting limits:**
1. Select the card
2. Click **Edit Limits**
3. Adjust daily and/or monthly limits
4. Click **Save**

**Card features you can enable/disable:**
- International transactions
- Contactless payments
- E-commerce transactions

#### Loan Applications

1. Go to **Loans > Apply for Loan**
2. Select loan type:

| Loan Type | Purpose | Max Tenure |
|---|---|---|
| Personal | Unsecured personal expenses | 5 years |
| Home | Property purchase/construction | 20 years |
| Auto | Vehicle purchase | 7 years |
| Education | Higher education expenses | 15 years |
| Business | Business expansion/working capital | 10 years |

3. Enter the principal amount
4. Enter the desired tenure in months
5. The system calculates the estimated EMI automatically
6. Review the loan terms and interest rate
7. Submit the application
8. Track application status in **Loans > My Applications**

#### EMI Calculator

1. Go to **Loans > EMI Calculator**
2. Enter:

| Field | Description |
|---|---|
| Loan Amount | Principal amount you wish to borrow |
| Interest Rate | Annual interest rate (percentage) |
| Tenure | Repayment period in months |

3. The calculator shows:
   - Monthly EMI amount
   - Total interest payable
   - Total amount payable (principal + interest)
   - Amortization schedule (per-month breakdown)

```
┌────────────────────────────────────────────────────┐
│  EMI Calculator                                   │
│                                                    │
│  Loan Amount:  $500,000.00                        │
│  Interest Rate:  10.5%                            │
│  Tenure:  60 months                               │
│                                                    │
│  ──────────────────────────────────────            │
│                                                    │
│  Monthly EMI:          $10,748.06                 │
│  Total Interest:       $144,883.60                 │
│  Total Payable:        $644,883.60                 │
│                                                    │
│  [View Amortization Schedule]                     │
│                                                    │
│  ┌────────────────────────────┐                    │
│  │  ████████░░░░░░░░░░░░░░░  │  Principal        │
│  │  ░░░░░░░░███████████████  │  Interest         │
│  └────────────────────────────┘                    │
│   Year 1          Year 5                           │
└────────────────────────────────────────────────────┘
```

### Security

#### Behavioral Biometrics Explained

Behavioral biometrics is the science of identifying people by **how they do things**, not what they know (passwords) or what they have (phones). The platform analyzes:

**Keystroke Dynamics:**
- How fast you type (words per minute)
- How long you hold each key
- The rhythm between key presses
- Which keys you press (special keys, numbers, backspace)
- Error correction patterns (how you fix mistakes)

**Mouse Dynamics:**
- How fast you move the mouse
- Acceleration and deceleration patterns
- The shape of your mouse movements (curves vs. straight lines)
- Click patterns (single vs. double, left vs. right)
- Scroll behavior

**Session Patterns:**
- Time of day you typically bank
- How long your sessions last
- Navigation patterns between pages
- Form-filling behavior

**Mobile Touch (App):**
- Swipe velocity and acceleration
- Touch pressure
- Gesture complexity
- Multi-touch patterns
- Device orientation and handling

Your unique behavioral pattern creates a **behavioral fingerprint** that is extremely difficult to impersonate.

#### Trust Score

The trust score is a number from 0-100 that indicates how confident the system is that you are who you claim to be:

| Score Range | Meaning | Action |
|---|---|---|
| 0-30 | High trust | All actions allowed without additional verification |
| 31-70 | Moderate trust | Sensitive actions require MFA |
| 71-100 | Low trust | Actions blocked, fraud alert triggered |

**What affects your trust score:**
- **Positive factors:** Consistent typing/mouse pattern, trusted device, normal banking hours, familiar transaction amounts
- **Negative factors:** Different typing speed, new device, unusual time (3 AM), large or unusual transactions, different navigation pattern

Over time, as you use the platform, the system builds a more accurate profile and false challenges decrease.

#### Security Settings

Accessible via **Settings > Security**:

```
┌────────────────────────────────────────────────────┐
│  Security Settings                                 │
│                                                    │
│  Multi-Factor Authentication                       │
│  ┌──────────────────────────────────────────────┐  │
│  │  Status: ✅ Enabled (Authenticator App)      │  │
│  │  [Disable] [Change Method] [View Backup Codes]│  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  Password                                          │
│  ┌──────────────────────────────────────────────┐  │
│  │  Last changed: 30 days ago                   │  │
│  │  [Change Password]                          │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  Login Alerts                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  ☑ Email me when a new device logs in        │  │
│  │  ☑ Email me for transactions over $1,000     │  │
│  │  ☐ SMS me for all transactions              │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  Session Management                                │
│  ┌──────────────────────────────────────────────┐  │
│  │  Active sessions: 2                          │  │
│  │  [View Active Sessions] [Log Out All Devices]│  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

#### Device Management

View and manage devices that have accessed your account:

1. Go to **Settings > Security > Devices**
2. Each device shows: device name, browser, OS, last used, trust status
3. You can remove untrusted devices
4. Devices marked as "trusted" may skip MFA for low-risk actions

```
┌────────────────────────────────────────────────────┐
│  Registered Devices                                │
│                                                    │
│  ✅ Trusted                                        │
│  ┌──────────────────────────────────────────────┐  │
│  │  MacBook Pro · Chrome 120 · macOS 14.2      │  │
│  │  Last used: 2 hours ago · IP: 203.0.113.1  │  │
│  │  [Remove]                                   │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  iPhone 15 · Safari · iOS 17.2              │  │
│  │  Last used: 1 day ago · IP: 198.51.100.1   │  │
│  │  [Remove]                                   │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  ⚠ Untrusted                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Windows PC · Firefox 121 · Windows 11      │  │
│  │  Last used: 5 minutes ago · IP: 192.0.2.1  │  │
│  │  [Remove]                                   │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

#### Session Management

View and manage your active sessions:

1. Go to **Settings > Security > Sessions**
2. View all currently active sessions with device and location info
3. Click **Log Out** to terminate any session
4. Click **Log Out All Devices** to terminate all sessions except current

---

## Security Analyst Guide

### Dashboard Overview

#### Executive Overview

Access the dashboard at `https://dashboard.bbs-platform.com`

```
┌─────────────────────────────────────────────────────────────┐
│  🔐 Security Dashboard                     Last updated: 1m │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │ 1,520    │  │   234    │  │    47    │  │      5      │ │
│  │ Users    │  │ Sessions │  │ Alerts   │  │ Blocked Today│ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │
│                                                              │
│  Alerts by Severity           Risk Score Trend (7 days)      │
│  ┌────────────────────┐     ┌──────────────────────────┐    │
│  │ Critical:  3  ■■■  │     │ 30 ░░░░░░░░░░░░░░░░░░░░░ │    │
│  │ High:      8  ■■■■ │     │ 25 ░░░░░░░░░▒░░░░░░░░░░░ │    │
│  │ Medium:   15  ■■■■ │     │ 20 ░░░░▒░░░░░░░░░░░░░░░░ │    │
│  │ Low:      21  ■■■■ │     │ 15 ░░░░░░░░░░░░░░░░░░░░░ │    │
│  └────────────────────┘     │    M  T  W  T  F  S  S    │    │
│                              └──────────────────────────┘    │
│                                                              │
│  Risk Distribution           Model Health                    │
│  ┌────────────────────┐     ┌──────────────────────────┐    │
│  │ Very Low:  55.6%   │     │ Models in Production: 3  │    │
│  │ Low:       27.1%   │     │ Drifted Users:       12  │    │
│  │ Medium:    11.7%   │     │ Avg ML Accuracy:  94.2% │    │
│  │ High:       4.3%   │     │ Last Retrain:    2h ago │    │
│  │ Critical:   1.3%   │     └──────────────────────────┘    │
│  └────────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

**Key metrics:**

| Metric | Description | Alert Threshold |
|---|---|---|
| Users | Total registered users | - |
| Active Sessions | Currently active sessions | - |
| Alerts | Open fraud alerts by severity | Critical > 0 |
| Blocked Today | Transactions blocked by risk engine | - |
| Avg Risk Score | Mean risk score across all sessions | > 40 |
| Model Accuracy | Global model accuracy percentage | < 85% |
| Drifted Users | Users with behavioral drift detected | > 5% of users |

#### Understanding Risk Metrics

**Risk Score Components:**

| Component | Weight | Description |
|---|---|---|
| ML Score | 65% | Anomaly score from Isolation Forest model |
| Rules Score | 25% | Z-score deviations from personal baseline |
| Heuristic Score | 10% | Behavioral red flags (perfect typing, automation) |

**Risk Bands:**

| Band | Score | Decision | Description |
|---|---|---|---|
| Very Low | 0-15 | ALLOW | Highly confident this is the legitimate user |
| Low | 16-30 | ALLOW | Normal behavior, some minor deviations |
| Medium | 31-50 | ALLOW + MFA | Notable deviation, challenge with MFA |
| High | 51-70 | MFA + Review | Significant anomaly, require MFA and flag for review |
| Critical | 71-100 | BLOCK | Most likely fraudulent, block immediately |

### Investigation

#### Searching for Users

1. Use the search bar in the top navigation
2. Search by: email address, user ID, full name, phone number
3. Results show matching users with key details

```
┌──────────────────────────────────────────────────────────────┐
│  User Search                                    🔍 Search   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  johndoe@example.com                         [Search]│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Results (1):                                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  John Doe · johndoe@example.com · ID: 42             │   │
│  │  Status: Active · MFA: ✅ · Devices: 3 · Sessions: 47 │   │
│  │  Avg Risk: 22.3 · Last Login: 2h ago                 │   │
│  │  [View Profile] [View Alerts] [View Sessions]        │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

#### Analyzing Session Timelines

1. From a user's profile, click **View Sessions**
2. The session timeline shows all recent sessions chronologically:

```
┌──────────────────────────────────────────────────────────────┐
│  Session Timeline: John Doe                                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ ● Today, 10:30 AM - 11:15 AM (45 min)                    ││
│  │   IP: 203.0.113.1 · Device: MacBook Pro · Trusted: Yes   ││
│  │   Risk: ████████░░ 22.3 (LOW) · Events: 1,542           ││
│  │   Actions: Login, Balances, Transfer $500                ││
│  │   [View Details] [Explain Decision]                      ││
│  ├──────────────────────────────────────────────────────────┤│
│  │ ● Yesterday, 9:15 PM - 9:18 PM (3 min)                   ││
│  │   IP: 198.51.100.1 · Device: iPhone · Trusted: Yes       ││
│  │   Risk: ████████████ 45.0 (MEDIUM) · Events: 234         ││
│  │   Actions: Login, Check Balance (MFA prompted)           ││
│  │   [View Details] [Explain Decision]                      ││
│  ├──────────────────────────────────────────────────────────┤│
│  │ ● 2 days ago, 3:15 AM - 3:18 AM (3 min)                  ││
│  │   IP: 192.0.2.1 · Device: Windows PC · Trusted: No       ││
│  │   Risk: ████████████████████ 85.4 (HIGH) · Events: 245  ││
│  │   Actions: Login, Attempt Transfer $10,000 (BLOCKED)     ││
│  │   ⚠ Alert #501 - High Risk Transaction Blocked          ││
│  │   [View Details] [Explain Decision] [View Alert]         ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

3. Click **View Details** to see full session information:
   - All behavioral events (filterable by type)
   - Feature values extracted from the session
   - Risk score breakdown (ML, rules, heuristics)
   - Device fingerprint details
   - Geo-location data

4. Click **Explain Decision** to see the behavioral explanation:

```
┌──────────────────────────────────────────────────────────────┐
│  Decision Explanation - Session: sess_a1b2c3d4e5f6          │
│                                                              │
│  Overall Risk Score: 85.4 (HIGH) - Transaction BLOCKED      │
│                                                              │
│  Reasons:                                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 🔴 New device fingerprint detected (not in trusted     │ │
│  │    devices)                                             │ │
│  │ 🔴 Login at unusual time (3:00 AM)                     │ │
│  │ 🔴 Typing speed 3.2σ faster than personal baseline     │ │
│  │    (8.5 cps vs 5.8 cps)                                │ │
│  │ 🟡 Interaction density is 80% lower than typical       │ │
│  │    (0.5 vs 2.1 events/sec)                             │ │
│  │ 🟡 Perfect typing pattern with zero errors detected    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  Feature Contributions:                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ device_match:           -0.25  (highest impact)         │ │
│  │ typing_speed_mean:      -0.18                            │ │
│  │ time_of_day:            -0.15                            │ │
│  │ total_interactions:     -0.12                            │ │
│  │ backspace_rate:         -0.10                            │ │
│  │ cursor_velocity_mean:   -0.08                            │ │
│  │ session_duration:       -0.05                            │ │
│  │ navigation_entropy:     -0.03                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  Action Taken: BLOCK_AND_ALERT                               │
│  Alert #501 created - assigned to analyst queue             │
└──────────────────────────────────────────────────────────────┘
```

#### Reviewing Behavioral Profiles

1. From a user's profile, click **Behavioral Profile**
2. The profile shows:

```
┌──────────────────────────────────────────────────────────────┐
│  Behavioral Profile: John Doe                                │
│                                                              │
│  Status: ✅ Active · Version: 3 · Cold Start: No            │
│  Confidence: 87.5% · Sessions Analyzed: 47                  │
│  Drift Status: STABLE                                        │
│                                                              │
│  ┌──────────────── Keystroke Pattern ─────────────────────┐  │
│  │  Feature              Current     Baseline    Z-Score  │  │
│  │  Typing Speed         5.8 cps     5.5±0.9    0.33     │  │
│  │  Key Hold Duration    85ms        92±12      -0.58    │  │
│  │  Backspace Rate       0.03        0.05±0.02  -1.00    │  │
│  │  Error Correction     0.08        0.10±0.04  -0.50    │  │
│  │  Trigram Latency      520ms       480±85     0.47     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────── Mouse Pattern ───────────────────────┐  │
│  │  Feature              Current     Baseline    Z-Score  │  │
│  │  Cursor Velocity      3.2 px/ms   2.9±0.8    0.37     │  │
│  │  Click Frequency      0.05/s      0.04±0.02  0.50     │  │
│  │  Direction Entropy    2.1         2.3±0.4    -0.50    │  │
│  │  Scroll Speed         1.5         1.8±0.6    -0.50    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────── Risk History (30 days) ────────────────┐  │
│  │  25 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  │
│  │  20 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒░░░░░░░░░░░░░░  │  │
│  │  15 ░░░░░░░░░░░░▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  │
│  │  10 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  │
│  │     ───────────────────────────────────────────────    │  │
│  │     15  16  17  18  19  20  21  22  23  24  25  26  27│  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

#### Investigating Fraud Alerts

1. Navigate to **Alerts** in the sidebar
2. Use filters to narrow down alerts:

| Filter | Options | Description |
|---|---|---|
| Status | Open, Investigating, Resolved, False Positive, Dismissed | Current state |
| Severity | Info, Low, Medium, High, Critical | Alert severity |
| Date Range | Custom date range | When alert was created |
| User | Search by email/ID | Alerts for specific user |

3. Click an alert to view full details

**Alert Detail View:**

```
┌──────────────────────────────────────────────────────────────┐
│  Alert #501 - High Risk Transaction Blocked                  │
│  Severity: 🔴 HIGH · Status: OPEN                           │
│  Created: 2024-01-15 03:15 UTC · 2 hours ago                │
│                                                              │
│  ┌───────────────── Transaction Details ──────────────────┐  │
│  │  Amount: $10,000.00 to account ****9001               │  │
│  │  Type: External Transfer · Status: BLOCKED            │  │
│  │  Reference: TXN240115031500A1B2                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────── Session Details ─────────────────────┐  │
│  │  Duration: 3 min · Events: 245                        │  │
│  │  IP: 192.0.2.1 (Unknown Location)                     │  │
│  │  Device: Windows PC (New Device - Not Trusted)        │  │
│  │  User Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)│  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────── Risk Breakdown ──────────────────────┐  │
│  │  ML Score:     78.3 (high anomaly)                    │  │
│  │  Rules Score:  95.0 (typing, time, device triggered)  │  │
│  │  Heuristic:    60.0 (perfect typing, automation)      │  │
│  │  ─────────────────────────────────────                │  │
│  │  Final Score:  85.4 (HIGH)                            │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────── Anomaly Details ─────────────────────┐  │
│  │  Reason Code              Value    Threshold  Triggered│  │
│  │  untrusted_device         false    true        ✅     │  │
│  │  typing_speed_anomaly     3.2σ     2.0σ        ✅     │  │
│  │  suspicious_time          3:00 AM  10PM-5AM    ✅     │  │
│  │  perfect_typing           0 err     >0          ✅     │  │
│  │  automation_pattern       0.12      0.50        ✅     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  Actions:                                                    │
│  [Assign to Me] [Mark as Investigating]                     │
│  [Resolve - False Positive] [Resolve - Confirmed Fraud]     │
│  [Dismiss] [Add Note]                                       │
└──────────────────────────────────────────────────────────────┘
```

### ML Monitoring

#### Model Health Monitoring

Navigate to **ML > Model Health**:

```
┌──────────────────────────────────────────────────────────────┐
│  ML Model Health                                             │
│                                                              │
│  Global Model                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Version: global.20240115.000000                       │  │
│  │  Status: ✅ Healthy · Last Trained: 2h ago             │  │
│  │  Accuracy: 94.2% · Precision: 92.1% · Recall: 91.5%   │  │
│  │  Users Covered: 1,500 · Sessions: 45,000               │  │
│  │                                                         │  │
│  │  Population Drift: ░░░░░░░░░░ 0.02 PSI (STABLE)       │  │
│  │  Data Distribution: [Chart]                             │  │
│  │                                                         │  │
│  │  [Retrain] [View Details] [Rollback]                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  User Models Overview                                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Total Models:  1,480 (1,500 users, 20 cold start)    │  │
│  │  Active:        1,480                                 │  │
│  │  Drifted:       12 (0.8%) - Needs attention           │  │
│  │  Avg Threshold: -0.15                                  │  │
│  │                                                         │  │
│  │  Top Drifted Users:                                     │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ User ID  Drift Score  Feature     Z-Score       │   │  │
│  │  │ #42      0.35         typing_speed  3.2         │   │  │
│  │  │ #128     0.28         mouse_velocity 2.8        │   │  │
│  │  │ #55      0.22         session_dur   2.5         │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

#### Drift Detection

Drift is measured using the Population Stability Index (PSI):

| PSI Value | Severity | Action Required |
|---|---|---|
| < 0.10 | STABLE | No action |
| 0.10 - 0.25 | WARNING | Monitor, consider retraining |
| > 0.25 | CRITICAL | Immediate retraining required |

**Feature-level drift** is flagged when a single feature's distribution changes significantly. **Concept drift** is flagged when the overall model performance degrades.

**Drift causes:**
- New user population with different behavior patterns
- Platform UI changes (redesign affects navigation patterns)
- Seasonal patterns (holiday shopping behavior)
- Bot/automated access attempts
- Genuine user behavior change (new job, new device)

#### Retraining Management

**Automatic retraining triggers:**
1. Every 10 sessions per user (incremental personal model update)
2. When drift score exceeds PSI 0.25 (global model)
3. When accuracy drops by 10% (concept drift)
4. Scheduled daily maintenance window (cleanup and optimization)

**Manual retraining:**
```bash
# Via API
POST /api/admin/models/retrain
Authorization: Bearer <admin_token>
```

**Retraining workflow:**
1. System gathers all sessions since last training
2. Extracts features from raw behavioral events
3. Filters out high-risk sessions (risk score > MEDIUM max)
4. Concatenates with previous training data (up to 10,000 samples)
5. Trains Isolation Forest with adaptive thresholding
6. Saves model with version increment
7. Updates model registry
8. Invalidates model cache for affected users

### Alert Management

#### Reviewing Alerts

The alert queue prioritizes critical and high-severity alerts:

```
┌──────────────────────────────────────────────────────────────┐
│  Fraud Alerts                                Filters: [...] │
│                                                              │
│  ┌────┬────────┬──────────┬──────────┬────────┬──────────┐  │
│  │ ID │ Severity│ User     │ Type     │ Status │ Created  │  │
│  ├────┼────────┼──────────┼──────────┼────────┼──────────┤  │
│  │501 │ 🔴 H   │ John Doe │ High Risk│ Open   │ 03:15 AM │  │
│  │502 │ 🔴 H   │ Jane S.  │ New Dev  │ Open   │ 02:30 AM │  │
│  │503 │ 🟡 M   │ Bob J.   │ Typing   │ Invest │ 01:00 AM │  │
│  │504 │ 🟡 M   │ Alice W. │ Unusual  │ Open   │ 11:30 PM │  │
│  │505 │ 🟢 L   │ Charlie  │ Low Conf │ Resolv │ 10:00 PM │  │
│  └────┴────────┴──────────┴──────────┴────────┴──────────┘  │
│                                                              │
│  Showing 5 of 47 alerts                          [Load More] │
└──────────────────────────────────────────────────────────────┘
```

#### Investigating Suspicious Activity

Follow this workflow for each alert:

1. **Triage** (2 minutes)
   - Check severity and alert type
   - Review session timeline
   - Check if user has prior alerts

2. **Analyze** (5 minutes)
   - Review behavioral explanation
   - Check feature contributions
   - Compare against user's historical profile
   - Review device and location data
   - Check transaction history

3. **Decide** (1 minute)
   - **False Positive**: User behavior was valid but unusual (e.g., traveling abroad)
   - **Confirmed Fraud**: Clear indicators of account compromise
   - **Inconclusive**: Needs further investigation

#### Resolving and Dismissing Alerts

**Resolve as False Positive:**
```json
{
  "status": "false_positive",
  "resolution_notes": "User confirmed they were traveling abroad. Typing speed change due to mobile keyboard use. No compromise detected."
}
```

**Resolve as Confirmed Fraud:**
```json
{
  "status": "resolved",
  "resolution_notes": "Confirmed account takeover. User contacted support. Account locked, password reset, sessions terminated."
}
```

**Dismiss:**
```json
{
  "status": "dismissed",
  "resolution_notes": "Alert triggered by monitoring test. No action needed."
}
```

**Alert states:**

```
OPEN ──→ INVESTIGATING ──→ RESOLVED
  │                           │
  └──→ FALSE_POSITIVE         │
  └──→ DISMISSED ─────────────┘
```
