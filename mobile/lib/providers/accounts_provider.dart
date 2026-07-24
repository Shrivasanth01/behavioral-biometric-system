import 'package:flutter/foundation.dart';
import '../models/account_model.dart';
import '../models/transaction_model.dart';
import '../services/banking_service.dart';
import '../services/api_service.dart';

class AccountsProvider extends ChangeNotifier {
  final BankingService _bankingService = BankingService();

  List<AccountModel> _accounts = [];
  AccountModel? _selectedAccount;
  List<TransactionModel> _recentTransactions = [];
  bool _isLoading = false;
  String? _error;

  List<AccountModel> get accounts => _accounts;
  AccountModel? get selectedAccount => _selectedAccount;
  List<TransactionModel> get recentTransactions => _recentTransactions;
  bool get isLoading => _isLoading;
  String? get error => _error;

  double get totalBalance =>
      _accounts.fold(0.0, (sum, acc) => sum + acc.balance);

  double get totalAvailableBalance =>
      _accounts.fold(0.0, (sum, acc) => sum + acc.availableBalance);

  List<AccountModel> get activeAccounts =>
      _accounts.where((a) => a.isActive).toList();

  Future<void> loadAccounts() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _accounts = await _bankingService.getAccounts();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadAccountDetail(String accountId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _selectedAccount = await _bankingService.getAccountDetail(accountId);
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadRecentTransactions({String? accountId}) async {
    try {
      _recentTransactions = await _bankingService.getTransactions(
        accountId: accountId,
        limit: 10,
      );
      notifyListeners();
    } catch (e) {
      if (kDebugMode) {
        debugPrint('Failed to load transactions: $e');
      }
    }
  }

  Future<bool> transfer({
    required String fromAccountId,
    required String toAccountNumber,
    required double amount,
    String? description,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _bankingService.transfer(
        fromAccountId: fromAccountId,
        toAccountNumber: toAccountNumber,
        amount: amount,
        description: description,
      );
      await loadAccounts();
      await loadRecentTransactions(accountId: fromAccountId);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  void selectAccount(AccountModel account) {
    _selectedAccount = account;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
