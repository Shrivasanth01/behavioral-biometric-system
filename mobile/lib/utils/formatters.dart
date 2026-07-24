import 'package:intl/intl.dart';

class Formatters {
  static final NumberFormat _currencyFormat = NumberFormat.currency(
    symbol: '\$',
    decimalDigits: 2,
  );

  static final NumberFormat _compactFormat = NumberFormat.compact(
    locale: 'en_US',
  );

  static final NumberFormat _numberFormat = NumberFormat('#,##0.00');
  static final NumberFormat _integerFormat = NumberFormat('#,##0');
  static final DateFormat _dateFormat = DateFormat('MMM dd, yyyy');
  static final DateFormat _timeFormat = DateFormat('hh:mm a');
  static final DateFormat _dateTimeFormat = DateFormat('MMM dd, yyyy hh:mm a');
  static final DateFormat _shortDateFormat = DateFormat('MM/dd/yyyy');

  static String formatCurrency(double amount) {
    return _currencyFormat.format(amount);
  }

  static String formatCompact(double amount) {
    return '\$${_compactFormat.format(amount)}';
  }

  static String formatNumber(double value) {
    return _numberFormat.format(value);
  }

  static String formatInteger(int value) {
    return _integerFormat.format(value);
  }

  static String formatDate(DateTime date) {
    return _dateFormat.format(date);
  }

  static String formatTime(DateTime date) {
    return _timeFormat.format(date);
  }

  static String formatDateTime(DateTime date) {
    return _dateTimeFormat.format(date);
  }

  static String formatShortDate(DateTime date) {
    return _shortDateFormat.format(date);
  }

  static String formatRelativeTime(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return formatDate(date);
  }

  static String formatAccountNumber(String accountNumber) {
    if (accountNumber.isEmpty) return '';
    final buffer = StringBuffer();
    for (int i = 0; i < accountNumber.length; i++) {
      if (i > 0 && i % 4 == 0) {
        buffer.write(' ');
      }
      buffer.write(accountNumber[i]);
    }
    return buffer.toString();
  }

  static String maskCardNumber(String cardNumber) {
    if (cardNumber.length < 8) return cardNumber;
    return '${cardNumber.substring(0, 4)} **** **** ${cardNumber.substring(cardNumber.length - 4)}';
  }

  static String maskAccountNumber(String accountNumber) {
    if (accountNumber.length <= 4) return accountNumber;
    return 'XXXX${accountNumber.substring(accountNumber.length - 4)}';
  }

  static String formatPhoneNumber(String phone) {
    if (phone.length != 10) return phone;
    return '(${phone.substring(0, 3)}) ${phone.substring(3, 6)}-${phone.substring(6)}';
  }

  static String formatPercentage(double value) {
    return '${value.toStringAsFixed(2)}%';
  }

  static String formatTransactionType(String type) {
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
      default:
        return type[0].toUpperCase() + type.substring(1);
    }
  }

  static String formatStatus(String status) {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'reversed':
        return 'Reversed';
      case 'active':
        return 'Active';
      case 'inactive':
        return 'Inactive';
      case 'frozen':
        return 'Frozen';
      case 'closed':
        return 'Closed';
      case 'approved':
        return 'Approved';
      case 'rejected':
        return 'Rejected';
      default:
        return status[0].toUpperCase() + status.substring(1);
    }
  }

  static String capitalize(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1);
  }

  static String getInitials(String name) {
    if (name.isEmpty) return '?';
    final parts = name.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name[0].toUpperCase();
  }
}
