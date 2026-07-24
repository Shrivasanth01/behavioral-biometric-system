class BeneficiaryModel {
  final String id;
  final String userId;
  final String name;
  final String accountNumber;
  final String? ifscCode;
  final String bankName;
  final String? branchName;
  final String? nickname;
  final String? email;
  final String? phone;
  final String transferLimit;
  final bool isFavorite;
  final int transferCount;
  final DateTime createdAt;
  final DateTime? lastTransfer;

  BeneficiaryModel({
    required this.id,
    required this.userId,
    required this.name,
    required this.accountNumber,
    this.ifscCode,
    this.bankName = '',
    this.branchName,
    this.nickname,
    this.email,
    this.phone,
    this.transferLimit = 'daily',
    this.isFavorite = false,
    this.transferCount = 0,
    DateTime? createdAt,
    this.lastTransfer,
  }) : createdAt = createdAt ?? DateTime.now();

  factory BeneficiaryModel.fromJson(Map<String, dynamic> json) {
    return BeneficiaryModel(
      id: json['id'].toString(),
      userId: json['user_id']?.toString() ?? json['userId'] ?? '',
      name: json['name'] ?? '',
      accountNumber: json['account_number'] ?? json['accountNumber'] ?? '',
      ifscCode: json['ifsc_code'] ?? json['ifscCode'],
      bankName: json['bank_name'] ?? json['bankName'] ?? '',
      branchName: json['branch_name'] ?? json['branchName'],
      nickname: json['nickname'],
      email: json['email'],
      phone: json['phone'],
      transferLimit: json['transfer_limit'] ?? json['transferLimit'] ?? 'daily',
      isFavorite: json['is_favorite'] ?? json['isFavorite'] ?? false,
      transferCount: json['transfer_count'] ?? json['transferCount'] ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : (json['createdAt'] != null
              ? DateTime.parse(json['createdAt'])
              : DateTime.now()),
      lastTransfer: json['last_transfer'] != null
          ? DateTime.parse(json['last_transfer'])
          : (json['lastTransfer'] != null
              ? DateTime.parse(json['lastTransfer'])
              : null),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'name': name,
      'account_number': accountNumber,
      'ifsc_code': ifscCode,
      'bank_name': bankName,
      'branch_name': branchName,
      'nickname': nickname,
      'email': email,
      'phone': phone,
      'transfer_limit': transferLimit,
      'is_favorite': isFavorite,
      'transfer_count': transferCount,
      'created_at': createdAt.toIso8601String(),
      'last_transfer': lastTransfer?.toIso8601String(),
    };
  }

  String get displayName => nickname ?? name;
  String get maskedAccount {
    if (accountNumber.isEmpty) return '';
    if (accountNumber.length <= 4) return accountNumber;
    return 'XXXX${accountNumber.substring(accountNumber.length - 4)}';
  }
}
