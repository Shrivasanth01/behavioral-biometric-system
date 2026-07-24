import '../config/api_config.dart';
import '../models/account_model.dart';
import '../models/transaction_model.dart';
import '../models/card_model.dart';
import '../models/loan_model.dart';
import '../models/beneficiary_model.dart';
import 'api_service.dart';

class BankingService {
  final ApiService _api = ApiService();

  Future<List<AccountModel>> getAccounts() async {
    final response = await _api.get(ApiConfig.accounts);
    final list = response is List ? response : (response?['accounts'] ?? []);
    return list.map((e) => AccountModel.fromJson(e)).cast<AccountModel>().toList();
  }

  Future<AccountModel> getAccountDetail(String accountId) async {
    final response = await _api.get('${ApiConfig.accountDetail}$accountId');
    return AccountModel.fromJson(response ?? {});
  }

  Future<List<TransactionModel>> getTransactions({
    String? accountId,
    int page = 1,
    int limit = 20,
  }) async {
    final params = <String, String>{
      'page': page.toString(),
      'limit': limit.toString(),
    };
    if (accountId != null) {
      params['account_id'] = accountId;
    }
    final response = await _api.get(ApiConfig.transactions, queryParams: params);
    final list = response is List ? response : (response?['transactions'] ?? []);
    return list.map((e) => TransactionModel.fromJson(e)).cast<TransactionModel>().toList();
  }

  Future<TransactionModel> getTransactionDetail(String transactionId) async {
    final response = await _api.get('${ApiConfig.transactionDetail}$transactionId');
    return TransactionModel.fromJson(response ?? {});
  }

  Future<TransactionModel> transfer({
    required String fromAccountId,
    required String toAccountNumber,
    required double amount,
    String? description,
    String? category,
  }) async {
    final response = await _api.post(ApiConfig.transfer, body: {
      'from_account_id': fromAccountId,
      'to_account_number': toAccountNumber,
      'amount': amount,
      'description': description,
      'category': category,
    });
    return TransactionModel.fromJson(response ?? {});
  }

  Future<Map<String, dynamic>> makePayment({
    required String accountId,
    required String provider,
    required String consumerId,
    required double amount,
    String? description,
  }) async {
    final response = await _api.post(ApiConfig.payments, body: {
      'account_id': accountId,
      'provider': provider,
      'consumer_id': consumerId,
      'amount': amount,
      'description': description,
    });
    return response ?? {};
  }

  Future<List<CardModel>> getCards() async {
    final response = await _api.get(ApiConfig.cards);
    final list = response is List ? response : (response?['cards'] ?? []);
    return list.map((e) => CardModel.fromJson(e)).cast<CardModel>().toList();
  }

  Future<CardModel> getCardDetail(String cardId) async {
    final response = await _api.get('${ApiConfig.cardDetail}$cardId');
    return CardModel.fromJson(response ?? {});
  }

  Future<CardModel> createCard(Map<String, dynamic> data) async {
    final response = await _api.post(ApiConfig.cards, body: data);
    return CardModel.fromJson(response ?? {});
  }

  Future<CardModel> updateCardStatus(String cardId, String status) async {
    final response = await _api.put('${ApiConfig.cardDetail}$cardId', body: {
      'status': status,
    });
    return CardModel.fromJson(response ?? {});
  }

  Future<List<LoanModel>> getLoans() async {
    final response = await _api.get(ApiConfig.loans);
    final list = response is List ? response : (response?['loans'] ?? []);
    return list.map((e) => LoanModel.fromJson(e)).cast<LoanModel>().toList();
  }

  Future<LoanModel> getLoanDetail(String loanId) async {
    final response = await _api.get('${ApiConfig.loanDetail}$loanId');
    return LoanModel.fromJson(response ?? {});
  }

  Future<LoanModel> applyLoan(Map<String, dynamic> data) async {
    final response = await _api.post(ApiConfig.loanApply, body: data);
    return LoanModel.fromJson(response ?? {});
  }

  Future<List<BeneficiaryModel>> getBeneficiaries() async {
    final response = await _api.get(ApiConfig.beneficiaries);
    final list = response is List ? response : (response?['beneficiaries'] ?? []);
    return list.map((e) => BeneficiaryModel.fromJson(e)).cast<BeneficiaryModel>().toList();
  }

  Future<BeneficiaryModel> addBeneficiary(Map<String, dynamic> data) async {
    final response = await _api.post(ApiConfig.beneficiaries, body: data);
    return BeneficiaryModel.fromJson(response ?? {});
  }

  Future<void> deleteBeneficiary(String beneficiaryId) async {
    await _api.delete('${ApiConfig.beneficiaries}/$beneficiaryId');
  }

  Future<BeneficiaryModel> updateBeneficiary(
      String id, Map<String, dynamic> data) async {
    final response = await _api.put('${ApiConfig.beneficiaries}/$id', body: data);
    return BeneficiaryModel.fromJson(response ?? {});
  }
}
