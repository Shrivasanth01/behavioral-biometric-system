class UserModel {
  final String id;
  final String email;
  final String fullName;
  final String phone;
  final String? profileImage;
  final bool isMfaEnabled;
  final bool isBiometricEnabled;
  final double trustScore;
  final String kycStatus;
  final DateTime createdAt;
  final DateTime? lastLogin;

  UserModel({
    required this.id,
    required this.email,
    required this.fullName,
    required this.phone,
    this.profileImage,
    this.isMfaEnabled = false,
    this.isBiometricEnabled = false,
    this.trustScore = 0.0,
    this.kycStatus = 'pending',
    DateTime? createdAt,
    this.lastLogin,
  }) : createdAt = createdAt ?? DateTime.now();

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'].toString(),
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? json['fullName'] ?? '',
      phone: json['phone'] ?? '',
      profileImage: json['profile_image'],
      isMfaEnabled: json['is_mfa_enabled'] ?? json['isMfaEnabled'] ?? false,
      isBiometricEnabled:
          json['is_biometric_enabled'] ?? json['isBiometricEnabled'] ?? false,
      trustScore: (json['trust_score'] ?? json['trustScore'] ?? 0.0).toDouble(),
      kycStatus: json['kyc_status'] ?? json['kycStatus'] ?? 'pending',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : (json['createdAt'] != null
              ? DateTime.parse(json['createdAt'])
              : DateTime.now()),
      lastLogin: json['last_login'] != null
          ? DateTime.parse(json['last_login'])
          : (json['lastLogin'] != null
              ? DateTime.parse(json['lastLogin'])
              : null),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'phone': phone,
      'profile_image': profileImage,
      'is_mfa_enabled': isMfaEnabled,
      'is_biometric_enabled': isBiometricEnabled,
      'trust_score': trustScore,
      'kyc_status': kycStatus,
      'created_at': createdAt.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
    };
  }

  UserModel copyWith({
    String? id,
    String? email,
    String? fullName,
    String? phone,
    String? profileImage,
    bool? isMfaEnabled,
    bool? isBiometricEnabled,
    double? trustScore,
    String? kycStatus,
    DateTime? createdAt,
    DateTime? lastLogin,
  }) {
    return UserModel(
      id: id ?? this.id,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      phone: phone ?? this.phone,
      profileImage: profileImage ?? this.profileImage,
      isMfaEnabled: isMfaEnabled ?? this.isMfaEnabled,
      isBiometricEnabled: isBiometricEnabled ?? this.isBiometricEnabled,
      trustScore: trustScore ?? this.trustScore,
      kycStatus: kycStatus ?? this.kycStatus,
      createdAt: createdAt ?? this.createdAt,
      lastLogin: lastLogin ?? this.lastLogin,
    );
  }
}
