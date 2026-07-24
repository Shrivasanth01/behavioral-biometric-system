class ApiConfig {
  static const String baseUrl = 'http://10.0.2.2:8000/api';
  static const String wsUrl = 'ws://10.0.2.2:8000/ws';

  static const Duration timeout = Duration(seconds: 30);
  static const Duration behavioralUploadInterval = Duration(seconds: 15);

  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String verifyOtp = '/auth/verify-otp';
  static const String forgotPassword = '/auth/forgot-password';
  static const String resetPassword = '/auth/reset-password';
  static const String mfaSetup = '/auth/mfa/setup';
  static const String mfaVerify = '/auth/mfa/verify';
  static const String refreshToken = '/auth/refresh';

  static const String accounts = '/accounts';
  static const String accountDetail = '/accounts/';
  static const String transactions = '/transactions';
  static const String transactionDetail = '/transactions/';
  static const String transfer = '/transactions/transfer';
  static const String beneficiaries = '/beneficiaries';
  static const String cards = '/cards';
  static const String cardDetail = '/cards/';
  static const String loans = '/loans';
  static const String loanDetail = '/loans/';
  static const String loanApply = '/loans/apply';
  static const String payments = '/payments';
  static const String payment = '/payments/';

  static const String behavioralEvents = '/behavioral/events';
  static const String behavioralProfile = '/behavioral/profile';
  static const String behavioralScore = '/behavioral/trust-score';
  static const String behavioralVerify = '/behavioral/verify';

  static const String profile = '/users/profile';
  static const String updateProfile = '/users/profile/update';
  static const String notificationSettings = '/users/notifications';
}
