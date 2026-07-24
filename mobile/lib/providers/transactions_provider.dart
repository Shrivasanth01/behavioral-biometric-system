import 'package:flutter/foundation.dart';
import '../models/transaction_model.dart';
import '../services/banking_service.dart';

class TransactionsProvider extends ChangeNotifier {
  final BankingService _bankingService = BankingService();

  List<TransactionModel> _transactions = [];
  TransactionModel? _selectedTransaction;
  bool _isLoading = false;
  bool _hasMore = true;
  int _currentPage = 1;
  String? _error;
  String? _filterAccountId;
  String? _filterType;

  List<TransactionModel> get transactions => _transactions;
  TransactionModel? get selectedTransaction => _selectedTransaction;
  bool get isLoading => _isLoading;
  bool get hasMore => _hasMore;
  String? get error => _error;
  String? get filterAccountId => _filterAccountId;
  String? get filterType => _filterType;

  List<TransactionModel> get recentTransactions {
    if (_transactions.length > 5) return _transactions.sublist(0, 5);
    return _transactions;
  }

  List<TransactionModel> get credits =>
      _transactions.where((t) => t.isCredit).toList();
  List<TransactionModel> get debits =>
      _transactions.where((t) => t.isDebit).toList();

  double get totalCredits =>
      credits.fold(0.0, (sum, t) => sum + t.amount);
  double get totalDebits =>
      debits.fold(0.0, (sum, t) => sum + t.amount);

  Future<void> loadTransactions({bool refresh = false}) async {
    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
      _transactions.clear();
    }

    if (!_hasMore || _isLoading) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final newTransactions = await _bankingService.getTransactions(
        accountId: _filterAccountId,
        page: _currentPage,
        limit: 20,
      );

      if (newTransactions.length < 20) {
        _hasMore = false;
      }

      _transactions.addAll(newTransactions);
      _currentPage++;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadTransactionDetail(String transactionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _selectedTransaction =
          await _bankingService.getTransactionDetail(transactionId);
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  void setAccountFilter(String? accountId) {
    _filterAccountId = accountId;
    loadTransactions(refresh: true);
  }

  void setTypeFilter(String? type) {
    _filterType = type;
    notifyListeners();
  }

  void clearFilters() {
    _filterAccountId = null;
    _filterType = null;
    loadTransactions(refresh: true);
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
