import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../models/loan_model.dart';
import '../../services/banking_service.dart';
import '../../widgets/loan_card.dart';
import '../../widgets/app_button.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/empty_state.dart';
import '../../utils/formatters.dart';
import '../../utils/constants.dart';
import '../../utils/behavioral_capture.dart';

class LoansScreen extends StatefulWidget {
  const LoansScreen({super.key});

  @override
  State<LoansScreen> createState() => _LoansScreenState();
}

class _LoansScreenState extends State<LoansScreen> {
  final BankingService _bankingService = BankingService();
  List<LoanModel> _loans = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadLoans();
  }

  Future<void> _loadLoans() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      _loans = await _bankingService.getLoans();
    } catch (e) {
      _error = e.toString();
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Loans'),
          actions: [
            IconButton(
              icon: const Icon(Icons.calculate_outlined),
              onPressed: () {
                Navigator.pushNamed(context, '/emi-calculator');
              },
            ),
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: () => _showApplyLoanDialog(),
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: _loadLoans,
          child: _isLoading && _loans.isEmpty
              ? const LoadingIndicator(message: 'Loading loans...')
              : _loans.isEmpty
                  ? const EmptyState(
                      icon: Icons.account_balance_outlined,
                      title: 'No loans',
                      subtitle:
                          'Apply for a loan that suits your needs',
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _loans.length + 1,
                      itemBuilder: (context, index) {
                        if (index == 0) {
                          return _buildLoanSummary();
                        }
                        final loan = _loans[index - 1];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: LoanCard(
                            loan: loan,
                            onTap: () {
                              Navigator.pushNamed(
                                context,
                                '/loan-detail',
                                arguments: loan.id,
                              );
                            },
                          ),
                        );
                      },
                    ),
        ),
      ),
    );
  }

  Widget _buildLoanSummary() {
    final totalPrincipal =
        _loans.fold(0.0, (sum, l) => sum + l.principalAmount);
    final totalRemaining =
        _loans.fold(0.0, (sum, l) => sum + l.remainingAmount);
    final totalEmi = _loans.fold(0.0, (sum, l) => sum + l.monthlyEmi);

    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF4A148C),
            Color(0xFF6A1B9A),
            Color(0xFF8E24AA),
          ],
        ),
        borderRadius: BorderRadius.circular(ThemeConfig.borderRadius),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Loan Summary',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildSummaryItem('Total Loans', _loans.length.toString()),
              _buildSummaryItem(
                  'Total EMI', Formatters.formatCurrency(totalEmi)),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildSummaryItem(
                  'Principal', Formatters.formatCurrency(totalPrincipal)),
              _buildSummaryItem(
                  'Outstanding', Formatters.formatCurrency(totalRemaining)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.white60, fontSize: 12),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 17,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  void _showApplyLoanDialog() {
    final formKey = GlobalKey<FormState>();
    final amountController = TextEditingController();
    final purposeController = TextEditingController();
    String selectedType = 'Personal Loan';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.fromLTRB(
            24,
            24,
            24,
            24 + MediaQuery.of(ctx).viewInsets.bottom,
          ),
          child: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                  margin: const EdgeInsets.only(bottom: 20),
                  alignment: Alignment.center,
                ),
                const Text(
                  'Apply for Loan',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 20),
                DropdownButtonFormField<String>(
                  value: selectedType,
                  decoration: const InputDecoration(
                    labelText: 'Loan Type',
                    prefixIcon: Icon(Icons.category),
                  ),
                  items: AppConstants.loanTypes
                      .map((t) =>
                          DropdownMenuItem(value: t, child: Text(t)))
                      .toList(),
                  onChanged: (v) => selectedType = v ?? selectedType,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: amountController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Loan Amount',
                    prefixIcon: Icon(Icons.monetization_on),
                    prefix: Text('\$ '),
                  ),
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Required';
                    final amt = double.tryParse(v);
                    if (amt == null || amt <= 0) return 'Invalid amount';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: purposeController,
                  maxLines: 2,
                  decoration: const InputDecoration(
                    labelText: 'Purpose',
                    prefixIcon: Icon(Icons.description),
                    hintText: 'Why do you need this loan?',
                  ),
                ),
                const SizedBox(height: 20),
                AppButton(
                  text: 'Submit Application',
                  onPressed: () {
                    if (formKey.currentState!.validate()) {
                      Navigator.pop(ctx);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Loan application submitted!'),
                          backgroundColor: ThemeConfig.successColor,
                        ),
                      );
                    }
                  },
                ),
                const SizedBox(height: 16),
              ],
            ),
          ),
        );
      },
    );
  }
}
