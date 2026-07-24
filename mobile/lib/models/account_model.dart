class AccountModel {
  final String id;
  final String userId;
  final String accountNumber;
  final String accountType;
  final String accountName;
  final double balance;
  final double availableBalance;
  final String currency;
  final String status;
  final List<String> features;
  final DateTime createdAt;
  final DateTime? lastTransaction;

  AccountModel({
    required this.id,
    required this.userId,
    required this.accountNumber,
    required this.accountType,
    this.accountName = '',
    this.balance = 0.0,
    this.availableBalance = 0.0,
    this.currency = 'USD',
    this.status = 'active',
    this.features = const [],
    DateTime? createdAt,
    this.lastTransaction,
  }) : createdAt = createdAt ?? DateTime.now();

  factory AccountModel.fromJson(Map<String, dynamic> json) {
    return AccountModel(
      id: json['id'].toString(),
      userId: json['user_id']?.toString() ?? json['userId'] ?? '',
      accountNumber: json['account_number'] ?? json['accountNumber'] ?? '',
      accountType: json['account_type'] ?? json['accountType'] ?? 'savings',
      accountName: json['account_name'] ?? json['accountName'] ?? '',
      balance: (json['balance'] ?? 0.0).toDouble(),
      availableBalance:
          (json['available_balance'] ?? json['availableBalance'] ?? 0.0).toDouble(),
      currency: json['currency'] ?? 'USD',
      status: json['status'] ?? 'active',
      features: (json['features'] ?? []).cast<String>(),
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : (json['createdAt'] != null
              ? DateTime.parse(json['createdAt'])
              : DateTime.now()),
      lastTransaction: json['last_transaction'] != null
          ? DateTime.parse(json['last_transaction'])
          : (json['lastTransaction'] != null
              ? DateTime.parse(json['lastTransaction'])
              : null),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'account_number': accountNumber,
      'account_type': accountType,
      'account_name': accountName,
      'balance': balance,
      'available_balance': availableBalance,
      'currency': currency,
      'status': status,
      'features': features,
      'created_at': createdAt.toIso8601String(),
      'last_transaction': lastTransaction?.toIso8601String(),
    };
  }

  String get maskedAccountNumber {
    if (accountNumber.length <= 4) return accountNumber;
    return '****${accountNumber.substring(accountNumber.length - 4)}';
  }

  bool get isActive => status == 'active';
  bool get isFrozen => status == 'frozen';
  bool get isClosed => status == 'closed';
}
