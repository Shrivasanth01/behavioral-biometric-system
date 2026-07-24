import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/accounts_provider.dart';
import '../../widgets/app_button.dart';
import '../../widgets/loading_overlay.dart';
import '../../utils/constants.dart';
import '../../utils/behavioral_capture.dart';

class PaymentsScreen extends StatefulWidget {
  const PaymentsScreen({super.key});

  @override
  State<PaymentsScreen> createState() => _PaymentsScreenState();
}

class _PaymentsScreenState extends State<PaymentsScreen> {
  String _selectedCategory = 'bill';
  String? _selectedProvider;
  String? _selectedAccountId;
  final _consumerIdController = TextEditingController();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AccountsProvider>().loadAccounts();
    });
  }

  @override
  void dispose() {
    _consumerIdController.dispose();
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _makePayment() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedAccountId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select account')),
      );
      return;
    }
    if (_selectedProvider == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select provider')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final accountsProvider = context.read<AccountsProvider>();
      await accountsProvider.transfer(
        fromAccountId: _selectedAccountId!,
        toAccountNumber: _selectedProvider!,
        amount: double.parse(_amountController.text.trim()),
        description: _descriptionController.text.isNotEmpty
            ? _descriptionController.text.trim()
            : '$_selectedCategory payment',
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Payment successful!'),
          backgroundColor: ThemeConfig.successColor,
        ),
      );
      _consumerIdController.clear();
      _amountController.clear();
      _descriptionController.clear();
      setState(() {
        _selectedProvider = null;
        _selectedAccountId = null;
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Payment failed: $e')),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  List<String> _getProviders() {
    switch (_selectedCategory) {
      case 'bill':
        return AppConstants.billPaymentProviders;
      case 'mobile':
        return AppConstants.mobileRechargeOperators;
      case 'dth':
        return AppConstants.dthOperators;
      default:
        return [];
    }
  }

  @override
  Widget build(BuildContext context) {
    final accountsProvider = context.watch<AccountsProvider>();
    final providers = _getProviders();

    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Payments & Recharge'),
        ),
        body: LoadingOverlay(
          isLoading: _isLoading,
          message: 'Processing payment...',
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      _buildCategoryTab(
                        'Bill Payment',
                        Icons.receipt_long,
                        'bill',
                      ),
                      const SizedBox(width: 8),
                      _buildCategoryTab(
                        'Mobile',
                        Icons.phone_android,
                        'mobile',
                      ),
                      const SizedBox(width: 8),
                      _buildCategoryTab(
                        'DTH',
                        Icons.tv,
                        'dth',
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  DropdownButtonFormField<String>(
                    value: _selectedAccountId,
                    decoration: const InputDecoration(
                      labelText: 'Pay From',
                      prefixIcon: Icon(Icons.account_balance),
                    ),
                    items: accountsProvider.accounts
                        .map((acc) => DropdownMenuItem(
                              value: acc.id,
                              child: Text(
                                '${acc.accountName} - ${acc.maskedAccountNumber}',
                                style: const TextStyle(fontSize: 13),
                              ),
                            ))
                        .toList(),
                    onChanged: (v) =>
                        setState(() => _selectedAccountId = v),
                    validator: (v) =>
                        v == null ? 'Select account' : null,
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    value: _selectedProvider,
                    decoration: InputDecoration(
                      labelText: '${_selectedCategory == 'bill' ? 'Bill' : _selectedCategory == 'mobile' ? 'Operator' : 'DTH'} Provider',
                      prefixIcon: const Icon(Icons.business),
                    ),
                    items: providers
                        .map((p) =>
                            DropdownMenuItem(value: p, child: Text(p)))
                        .toList(),
                    onChanged: (v) =>
                        setState(() => _selectedProvider = v),
                    validator: (v) =>
                        v == null ? 'Select provider' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _consumerIdController,
                    textInputAction: TextInputAction.next,
                    decoration: InputDecoration(
                      labelText: _selectedCategory == 'mobile'
                          ? 'Mobile Number'
                          : _selectedCategory == 'dth'
                              ? 'Subscriber ID'
                              : 'Consumer ID',
                      prefixIcon: Icon(
                        _selectedCategory == 'mobile'
                            ? Icons.phone
                            : _selectedCategory == 'dth'
                                ? Icons.tv
                                : Icons.person,
                      ),
                      hintText: 'Enter ${_selectedCategory == 'mobile' ? 'mobile number' : 'ID'}',
                    ),
                    validator: (v) =>
                        v == null || v.isEmpty ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _amountController,
                    keyboardType: TextInputType.number,
                    textInputAction: TextInputAction.next,
                    decoration: const InputDecoration(
                      labelText: 'Amount',
                      prefixIcon: Icon(Icons.monetization_on_outlined),
                      hintText: '0.00',
                      prefix: Text('\$ '),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) return 'Amount required';
                      final amount = double.tryParse(v);
                      if (amount == null || amount <= 0) {
                        return 'Enter valid amount';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _descriptionController,
                    textInputAction: TextInputAction.done,
                    decoration: const InputDecoration(
                      labelText: 'Description (Optional)',
                      prefixIcon: Icon(Icons.description_outlined),
                      hintText: 'Payment description',
                    ),
                  ),
                  const SizedBox(height: 32),
                  AppButton(
                    text: _selectedCategory == 'mobile'
                        ? 'Recharge Now'
                        : 'Pay Now',
                    onPressed: _makePayment,
                    isLoading: _isLoading,
                    icon: Icons.payment,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCategoryTab(String label, IconData icon, String category) {
    final isSelected = _selectedCategory == category;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _selectedCategory = category),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected
                ? ThemeConfig.primaryColor
                : ThemeConfig.cardColor,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: isSelected
                  ? ThemeConfig.primaryColor
                  : ThemeConfig.dividerColor,
            ),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                color: isSelected ? Colors.white : ThemeConfig.textSecondary,
                size: 24,
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w500,
                  color: isSelected ? Colors.white : ThemeConfig.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
