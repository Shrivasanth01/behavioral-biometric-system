import 'package:flutter_test/flutter_test.dart';
import 'package:behavioral_biometric_banking/utils/validators.dart';
import 'package:behavioral_biometric_banking/utils/formatters.dart';

void main() {
  group('Validators', () {
    group('validateEmail', () {
      test('returns null for valid email', () {
        expect(Validators.validateEmail('test@example.com'), isNull);
      });

      test('returns error for empty email', () {
        expect(Validators.validateEmail(''), isNotNull);
      });

      test('returns error for invalid email', () {
        expect(Validators.validateEmail('not-an-email'), isNotNull);
      });

      test('returns error for null email', () {
        expect(Validators.validateEmail(null), isNotNull);
      });
    });

    group('validatePassword', () {
      test('returns null for strong password', () {
        expect(Validators.validatePassword('StrongP@ss1'), isNull);
      });

      test('returns error for short password', () {
        expect(Validators.validatePassword('Ab1'), isNotNull);
      });

      test('returns error for no uppercase', () {
        expect(Validators.validatePassword('password1'), isNotNull);
      });

      test('returns error for no digit', () {
        expect(Validators.validatePassword('Password'), isNotNull);
      });

      test('returns error for null', () {
        expect(Validators.validatePassword(null), isNotNull);
      });
    });

    group('validateConfirmPassword', () {
      test('returns null when passwords match', () {
        expect(Validators.validateConfirmPassword('pass123', 'pass123'), isNull);
      });

      test('returns error when passwords differ', () {
        expect(Validators.validateConfirmPassword('pass123', 'pass456'), isNotNull);
      });

      test('returns error for null', () {
        expect(Validators.validateConfirmPassword(null, 'pass'), isNotNull);
      });
    });

    group('validatePhone', () {
      test('returns null for valid phone', () {
        expect(Validators.validatePhone('+911234567890'), isNull);
      });

      test('returns error for short phone', () {
        expect(Validators.validatePhone('123'), isNotNull);
      });

      test('returns error for null', () {
        expect(Validators.validatePhone(null), isNotNull);
      });
    });

    group('validateName', () {
      test('returns null for valid name', () {
        expect(Validators.validateName('Rahul Sharma'), isNull);
      });

      test('returns error for short name', () {
        expect(Validators.validateName('A'), isNotNull);
      });

      test('returns error for empty name', () {
        expect(Validators.validateName(''), isNotNull);
      });

      test('returns error for null', () => {
        expect(Validators.validateName(null), isNotNull);
      });
    });

    group('validateAmount', () {
      test('returns null for valid amount', () {
        expect(Validators.validateAmount('5000'), isNull);
      });

      test('returns error for zero', () {
        expect(Validators.validateAmount('0'), isNotNull);
      });

      test('returns error for negative', () {
        expect(Validators.validateAmount('-100'), isNotNull);
      });

      test('returns error for non-numeric', () {
        expect(Validators.validateAmount('abc'), isNotNull);
      });

      test('returns error for null', () {
        expect(Validators.validateAmount(null), isNotNull);
      });
    });

    group('validateAccountNumber', () {
      test('returns null for valid account number', () {
        expect(Validators.validateAccountNumber('12345678901'), isNull);
      });

      test('returns error for too short', () {
        expect(Validators.validateAccountNumber('12345'), isNotNull);
      });
    });

    group('validateIfscCode', () {
      test('returns null for valid IFSC', () {
        expect(Validators.validateIfscCode('SBIN0001234'), isNull);
      });

      test('returns error for invalid IFSC', () => {
        expect(Validators.validateIfscCode('SBIN123'), isNotNull);
      });
    });

    group('validateOtp', () {
      test('returns null for 6-digit OTP', () {
        expect(Validators.validateOtp('123456'), isNull);
      });

      test('returns error for non-numeric', () {
        expect(Validators.validateOtp('abcdef'), isNotNull);
      });

      test('returns error for wrong length', () {
        expect(Validators.validateOtp('12345'), isNotNull);
      });
    });

    group('validatePin', () {
      test('returns null for 4-digit PIN', () {
        expect(Validators.validatePin('1234'), isNull);
      });

      test('returns error for wrong length', () {
        expect(Validators.validatePin('123'), isNotNull);
      });
    });

    group('validateCardNumber', () {
      test('returns null for 16 digits', () {
        expect(Validators.validateCardNumber('4532015112890346'), isNull);
      });

      test('returns null with spaces', () {
        expect(Validators.validateCardNumber('4532 0151 1289 0346'), isNull);
      });

      test('returns error for wrong length', () {
        expect(Validators.validateCardNumber('1234'), isNotNull);
      });
    });

    group('validateCvv', () {
      test('returns null for 3-digit CVV', () {
        expect(Validators.validateCvv('123'), isNull);
      });

      test('returns null for 4-digit CVV', () {
        expect(Validators.validateCvv('1234'), isNull);
      });

      test('returns error for non-numeric', () {
        expect(Validators.validateCvv('abc'), isNotNull);
      });
    });

    group('validateExpiryDate', () {
      test('returns null for future MM/YY', () {
        final future = DateTime.now().add(const Duration(days: 365));
        final mm = future.month.toString().padLeft(2, '0');
        final yy = future.year.toString().substring(2);
        expect(Validators.validateExpiryDate('$mm/$yy'), isNull);
      });

      test('returns error for invalid format', () {
        expect(Validators.validateExpiryDate('13/25'), isNotNull);
      });
    });

    group('validateRequired', () {
      test('returns null for non-empty', () {
        expect(Validators.validateRequired('hello', 'Field'), isNull);
      });

      test('returns error for empty', () {
        expect(Validators.validateRequired('', 'Field'), isNotNull);
      });

      test('returns error for whitespace', () {
        expect(Validators.validateRequired('   ', 'Field'), isNotNull);
      });
    });
  });

  group('Formatters', () {
    group('formatCurrency', () {
      test('formats positive amount', () {
        expect(Formatters.formatCurrency(1234.56), contains('\$'));
      });

      test('formats zero', () {
        expect(Formatters.formatCurrency(0), contains('0.00'));
      });
    });

    group('formatCompact', () {
      test('formats thousands', () {
        expect(Formatters.formatCompact(1500), contains('\$'));
      });
    });

    group('formatDate', () {
      test('formats DateTime', () {
        final date = DateTime(2024, 6, 14);
        expect(Formatters.formatDate(date), contains('Jun'));
      });
    });

    group('formatRelativeTime', () {
      test('returns Just now for recent', () {
        expect(Formatters.formatRelativeTime(DateTime.now()), contains('Just now'));
      });

      test('returns minutes for recent past', () {
        final past = DateTime.now().subtract(const Duration(minutes: 5));
        expect(Formatters.formatRelativeTime(past), contains('m ago'));
      });
    });

    group('maskCardNumber', () {
      test('masks middle digits', () {
        expect(Formatters.maskCardNumber('4532015112890346'), contains('****'));
      });

      test('returns short numbers unchanged', () {
        expect(Formatters.maskCardNumber('1234'), '1234');
      });
    });

    group('maskAccountNumber', () {
      test('masks all but last 4', () {
        expect(Formatters.maskAccountNumber('12345678901'), 'XXXX8901');
      });
    });

    group('getInitials', () {
      test('extracts two initials', () {
        expect(Formatters.getInitials('Rahul Sharma'), 'RS');
      });

      test('handles single name', () {
        expect(Formatters.getInitials('Rahul'), 'R');
      });

      test('handles empty string', () {
        expect(Formatters.getInitials(''), '?');
      });
    });

    group('formatPhoneNumber', () {
      test('formats 10-digit phone', () {
        expect(Formatters.formatPhoneNumber('9876543210'), contains('('));
      });

      test('returns non-10-digit unchanged', () {
        expect(Formatters.formatPhoneNumber('12345'), '12345');
      });
    });

    group('formatTransactionType', () {
      test('capitalizes known types', () {
        expect(Formatters.formatTransactionType('deposit'), 'Deposit');
        expect(Formatters.formatTransactionType('transfer'), 'Transfer');
      });

      test('capitalizes unknown types', () {
        expect(Formatters.formatTransactionType('unknown'), 'Unknown');
      });
    });

    group('formatStatus', () => {
      test('capitalizes known statuses', () {
        expect(Formatters.formatStatus('pending'), 'Pending');
        expect(Formatters.formatStatus('completed'), 'Completed');
        expect(Formatters.formatStatus('failed'), 'Failed');
      });
    });

    group('capitalize', () => {
      test('capitalizes first letter', () {
        expect(Formatters.capitalize('hello'), 'Hello');
      });

      test('handles empty string', () {
        expect(Formatters.capitalize(''), '');
      });
    });

    group('formatPercentage', () {
      test('formats percentage', () {
        expect(Formatters.formatPercentage(12.5), '12.50%');
      });
    });
  });
}
