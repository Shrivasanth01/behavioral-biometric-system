class TransactionModel {
  final String id;
  final String accountId;
  final String type;
  final double amount;
  final double fee;
  final double balanceBefore;
  final double balanceAfter;
  final String status;
  final String description;
  final String? referenceNumber;
  final String? counterpartyName;
  final String? counterpartyAccount;
  final String? category;
  final String? paymentMethod;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime? completedAt;

  TransactionModel({
    required this.id,
    required this.accountId,
    required this.type,
    required this.amount,
    this.fee = 0.0,
    this.balanceBefore = 0.0,
    this.balanceAfter = 0.0,
    this.status = 'pending',
    this.description = '',
    this.referenceNumber,
    this.counterpartyName,
    this.counterpartyAccount,
    this.category,
    this.paymentMethod,
    this.metadata,
    DateTime? createdAt,
    this.completedAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory TransactionModel.fromJson(Map<String, dynamic> json) {
    return TransactionModel(
      id: json['id'].toString(),
      accountId:
          json['account_id']?.toString() ?? json['accountId'] ?? '',
      type: json['type'] ?? 'transfer',
      amount: (json['amount'] ?? 0.0).toDouble(),
      fee: (json['fee'] ?? 0.0).toDouble(),
      balanceBefore:
          (json['balance_before'] ?? json['balanceBefore'] ?? 0.0).toDouble(),
      balanceAfter:
          (json['balance_after'] ?? json['balanceAfter'] ?? 0.0).toDouble(),
      status: json['status'] ?? 'pending',
      description: json['description'] ?? '',
      referenceNumber:
          json['reference_number'] ?? json['referenceNumber'],
      counterpartyName:
          json['counterparty_name'] ?? json['counterpartyName'],
      counterpartyAccount:
          json['counterparty_account'] ?? json['counterpartyAccount'],
      category: json['category'],
      paymentMethod: json['payment_method'] ?? json['paymentMethod'],
      metadata: json['metadata'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : (json['createdAt'] != null
              ? DateTime.parse(json['createdAt'])
              : DateTime.now()),
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : (json['completedAt'] != null
              ? DateTime.parse(json['completedAt'])
              : null),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'account_id': accountId,
      'type': type,
      'amount': amount,
      'fee': fee,
      'balance_before': balanceBefore,
      'balance_after': balanceAfter,
      'status': status,
      'description': description,
      'reference_number': referenceNumber,
      'counterparty_name': counterpartyName,
      'counterparty_account': counterpartyAccount,
      'category': category,
      'payment_method': paymentMethod,
      'metadata': metadata,
      'created_at': createdAt.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
    };
  }

  bool get isCredit =>
      type == 'deposit' ||
      type == 'credit' ||
      type == 'refund' ||
      type == 'interest';
  bool get isDebit =>
      type == 'withdrawal' ||
      type == 'transfer' ||
      type == 'payment' ||
      type == 'fee';
  bool get isPending => status == 'pending';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isReversed => status == 'reversed';

  String get formattedType {
    switch (type) {
      case 'deposit':
        return 'Deposit';
      case 'withdrawal':
        return 'Withdrawal';
      case 'transfer':
        return 'Transfer';
      case 'payment':
        return 'Payment';
      case 'refund':
        return 'Refund';
      case 'interest':
        return 'Interest';
      case 'fee':
        return 'Fee';
      case 'credit':
        return 'Credit';
      default:
        return type;
    }
  }
}
