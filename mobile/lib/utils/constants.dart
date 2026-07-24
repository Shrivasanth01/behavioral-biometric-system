class AppConstants {
  static const String appName = 'SecureBank';
  static const String appVersion = '1.0.0';
  static const String appTagline = 'AI-Powered Behavioral Banking';

  static const double maxTransferAmount = 1000000.0;
  static const double minTransferAmount = 1.0;
  static const double maxLoanAmount = 10000000.0;
  static const double maxCardDailyLimit = 100000.0;
  static const double maxCardMonthlyLimit = 500000.0;

  static const int otpLength = 6;
  static const int pinLength = 4;
  static const int passwordMinLength = 8;
  static const int maxLoginAttempts = 5;

  static const Duration otpResendDuration = Duration(seconds: 30);
  static const Duration sessionTimeout = Duration(minutes: 15);
  static const Duration behavioralUploadInterval = Duration(seconds: 15);
  static const Duration sensorCollectionInterval = Duration(milliseconds: 100);

  static const List<String> transactionCategories = [
    'Food & Dining',
    'Shopping',
    'Transportation',
    'Utilities',
    'Entertainment',
    'Healthcare',
    'Education',
    'Travel',
    'Rent',
    'Salary',
    'Investment',
    'Transfer',
    'Other',
  ];

  static const List<String> billPaymentProviders = [
    'Electricity',
    'Water',
    'Gas',
    'Internet',
    'Telephone',
    'Insurance',
    'Tax',
    'Credit Card',
    'Loan',
    'Rent',
    'Other',
  ];

  static const List<String> mobileRechargeOperators = [
    'Airtel',
    'Jio',
    'Vi',
    'BSNL',
    'MTNL',
  ];

  static const List<String> dthOperators = [
    'Tata Sky',
    'Dish TV',
    'Airtel Digital TV',
    'Sun Direct',
    'Videocon d2h',
  ];

  static const List<String> loanTypes = [
    'Personal Loan',
    'Home Loan',
    'Car Loan',
    'Education Loan',
    'Business Loan',
    'Gold Loan',
    'Loan Against Property',
    'Credit Card Loan',
  ];

  static const List<String> accountTypes = [
    'Savings',
    'Current',
    'Salary',
    'Fixed Deposit',
    'Recurring Deposit',
    'NRI Savings',
  ];

  static const List<String> cardNetworks = [
    'Visa',
    'Mastercard',
    'RuPay',
    'American Express',
  ];

  static const Map<String, double> loanInterestRates = {
    'Personal Loan': 10.99,
    'Home Loan': 6.75,
    'Car Loan': 7.50,
    'Education Loan': 8.40,
    'Business Loan': 12.00,
    'Gold Loan': 7.00,
    'Loan Against Property': 8.50,
    'Credit Card Loan': 14.00,
  };

  static const Map<String, int> loanMaxTenures = {
    'Personal Loan': 60,
    'Home Loan': 360,
    'Car Loan': 84,
    'Education Loan': 180,
    'Business Loan': 120,
    'Gold Loan': 36,
    'Loan Against Property': 240,
    'Credit Card Loan': 60,
  };
}
