class CardModel {
  final String id;
  final String accountId;
  final String cardNumber;
  final String cardHolderName;
  final String expiryMonth;
  final String expiryYear;
  final String cvv;
  final String cardType;
  final String network;
  final String status;
  final bool isVirtual;
  final bool isContactless;
  final double dailyLimit;
  final double monthlyLimit;
  final double spentToday;
  final double spentThisMonth;
  final String? colorHex;
  final DateTime createdAt;
  final DateTime? activatedAt;
  final DateTime? expiresAt;

  CardModel({
    required this.id,
    required this.accountId,
    required this.cardNumber,
    required this.cardHolderName,
    required this.expiryMonth,
    required this.expiryYear,
    this.cvv = '',
    this.cardType = 'debit',
    this.network = 'visa',
    this.status = 'active',
    this.isVirtual = false,
    this.isContactless = true,
    this.dailyLimit = 5000.0,
    this.monthlyLimit = 50000.0,
    this.spentToday = 0.0,
    this.spentThisMonth = 0.0,
    this.colorHex,
    DateTime? createdAt,
    this.activatedAt,
    this.expiresAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory CardModel.fromJson(Map<String, dynamic> json) {
    return CardModel(
      id: json['id'].toString(),
      accountId:
          json['account_id']?.toString() ?? json['accountId'] ?? '',
      cardNumber: json['card_number'] ?? json['cardNumber'] ?? '',
      cardHolderName:
          json['card_holder_name'] ?? json['cardHolderName'] ?? '',
      expiryMonth:
          json['expiry_month']?.toString() ?? json['expiryMonth'] ?? '',
      expiryYear:
          json['expiry_year']?.toString() ?? json['expiryYear'] ?? '',
      cvv: json['cvv'] ?? '',
      cardType: json['card_type'] ?? json['cardType'] ?? 'debit',
      network: json['network'] ?? 'visa',
      status: json['status'] ?? 'active',
      isVirtual: json['is_virtual'] ?? json['isVirtual'] ?? false,
      isContactless:
          json['is_contactless'] ?? json['isContactless'] ?? true,
      dailyLimit: (json['daily_limit'] ?? json['dailyLimit'] ?? 5000.0).toDouble(),
      monthlyLimit:
          (json['monthly_limit'] ?? json['monthlyLimit'] ?? 50000.0).toDouble(),
      spentToday:
          (json['spent_today'] ?? json['spentToday'] ?? 0.0).toDouble(),
      spentThisMonth:
          (json['spent_this_month'] ?? json['spentThisMonth'] ?? 0.0).toDouble(),
      colorHex: json['color_hex'] ?? json['colorHex'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : (json['createdAt'] != null
              ? DateTime.parse(json['createdAt'])
              : DateTime.now()),
      activatedAt: json['activated_at'] != null
          ? DateTime.parse(json['activated_at'])
          : (json['activatedAt'] != null
              ? DateTime.parse(json['activatedAt'])
              : null),
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'])
          : (json['expiresAt'] != null
              ? DateTime.parse(json['expiresAt'])
              : null),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'account_id': accountId,
      'card_number': cardNumber,
      'card_holder_name': cardHolderName,
      'expiry_month': expiryMonth,
      'expiry_year': expiryYear,
      'cvv': cvv,
      'card_type': cardType,
      'network': network,
      'status': status,
      'is_virtual': isVirtual,
      'is_contactless': isContactless,
      'daily_limit': dailyLimit,
      'monthly_limit': monthlyLimit,
      'spent_today': spentToday,
      'spent_this_month': spentThisMonth,
      'color_hex': colorHex,
      'created_at': createdAt.toIso8601String(),
      'activated_at': activatedAt?.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
    };
  }

  String get maskedCardNumber {
    if (cardNumber.isEmpty) return '****';
    if (cardNumber.length <= 4) return cardNumber;
    final last4 = cardNumber.substring(cardNumber.length - 4);
    return '**** **** **** $last4';
  }

  String get formattedExpiry => '$expiryMonth/$expiryYear';

  bool get isActive => status == 'active';
  bool get isBlocked => status == 'blocked';
  bool get isExpired => status == 'expired';

  Color get cardColor {
    if (colorHex != null && colorHex!.isNotEmpty) {
      try {
        final hex = colorHex!.replaceAll('#', '');
        return Color(int.parse('FF$hex', radix: 16));
      } catch (_) {}
    }
    switch (network) {
      case 'visa':
        return const Color(0xFF1A1F71);
      case 'mastercard':
        return const Color(0xFF231F20);
      case 'rupay':
        return const Color(0xFF1B9B4A);
      case 'amex':
        return const Color(0xFF2E77BC);
      default:
        return const Color(0xFF1A237E);
    }
  }
}
