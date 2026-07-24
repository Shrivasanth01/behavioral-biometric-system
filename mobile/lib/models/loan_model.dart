class LoanModel {
  final String id;
  final String accountId;
  final String loanType;
  final double principalAmount;
  final double remainingAmount;
  final double interestRate;
  final int tenureMonths;
  final int remainingMonths;
  final double monthlyEmi;
  final double totalPayable;
  final double totalInterest;
  final double amountPaid;
  final String status;
  final String? purpose;
  final String? collateralInfo;
  final double? lateFee;
  final DateTime? nextPaymentDate;
  final DateTime createdAt;
  final DateTime? approvedAt;
  final DateTime? closedAt;

  LoanModel({
    required this.id,
    required this.accountId,
    this.loanType = 'personal',
    required this.principalAmount,
    this.remainingAmount = 0.0,
    this.interestRate = 0.0,
    this.tenureMonths = 12,
    this.remainingMonths = 0,
    this.monthlyEmi = 0.0,
    this.totalPayable = 0.0,
    this.totalInterest = 0.0,
    this.amountPaid = 0.0,
    this.status = 'pending',
    this.purpose,
    this.collateralInfo,
    this.lateFee,
    this.nextPaymentDate,
    DateTime? createdAt,
    this.approvedAt,
    this.closedAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory LoanModel.fromJson(Map<String, dynamic> json) {
    return LoanModel(
      id: json['id'].toString(),
      accountId:
          json['account_id']?.toString() ?? json['accountId'] ?? '',
      loanType: json['loan_type'] ?? json['loanType'] ?? 'personal',
      principalAmount:
          (json['principal_amount'] ?? json['principalAmount'] ?? 0.0).toDouble(),
      remainingAmount:
          (json['remaining_amount'] ?? json['remainingAmount'] ?? 0.0).toDouble(),
      interestRate:
          (json['interest_rate'] ?? json['interestRate'] ?? 0.0).toDouble(),
      tenureMonths: json['tenure_months'] ?? json['tenureMonths'] ?? 12,
      remainingMonths:
          json['remaining_months'] ?? json['remainingMonths'] ?? 0,
      monthlyEmi:
          (json['monthly_emi'] ?? json['monthlyEmi'] ?? 0.0).toDouble(),
      totalPayable:
          (json['total_payable'] ?? json['totalPayable'] ?? 0.0).toDouble(),
      totalInterest:
          (json['total_interest'] ?? json['totalInterest'] ?? 0.0).toDouble(),
      amountPaid:
          (json['amount_paid'] ?? json['amountPaid'] ?? 0.0).toDouble(),
      status: json['status'] ?? 'pending',
      purpose: json['purpose'],
      collateralInfo:
          json['collateral_info'] ?? json['collateralInfo'],
      lateFee: (json['late_fee'] ?? json['lateFee'])?.toDouble(),
      nextPaymentDate: json['next_payment_date'] != null
          ? DateTime.parse(json['next_payment_date'])
          : (json['nextPaymentDate'] != null
              ? DateTime.parse(json['nextPaymentDate'])
              : null),
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : (json['createdAt'] != null
              ? DateTime.parse(json['createdAt'])
              : DateTime.now()),
      approvedAt: json['approved_at'] != null
          ? DateTime.parse(json['approved_at'])
          : (json['approvedAt'] != null
              ? DateTime.parse(json['approvedAt'])
              : null),
      closedAt: json['closed_at'] != null
          ? DateTime.parse(json['closed_at'])
          : (json['closedAt'] != null
              ? DateTime.parse(json['closedAt'])
              : null),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'account_id': accountId,
      'loan_type': loanType,
      'principal_amount': principalAmount,
      'remaining_amount': remainingAmount,
      'interest_rate': interestRate,
      'tenure_months': tenureMonths,
      'remaining_months': remainingMonths,
      'monthly_emi': monthlyEmi,
      'total_payable': totalPayable,
      'total_interest': totalInterest,
      'amount_paid': amountPaid,
      'status': status,
      'purpose': purpose,
      'collateral_info': collateralInfo,
      'late_fee': lateFee,
      'next_payment_date': nextPaymentDate?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'approved_at': approvedAt?.toIso8601String(),
      'closed_at': closedAt?.toIso8601String(),
    };
  }

  bool get isPending => status == 'pending';
  bool get isApproved => status == 'approved';
  bool get isActive => status == 'active';
  bool get isClosed => status == 'closed';
  bool get isDefaulted => status == 'defaulted';

  double get progressPercent {
    if (totalPayable == 0) return 0;
    return (amountPaid / totalPayable).clamp(0.0, 1.0);
  }
}
