import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/accounts_provider.dart';
import '../../widgets/app_button.dart';
import '../../widgets/loading_overlay.dart';
import '../../utils/validators.dart';
import '../../utils/behavioral_capture.dart';

class TransfersScreen extends StatefulWidget {
  const TransfersScreen({super.key});

  @override
  State<TransfersScreen> createState() => _TransfersScreenState();
}

class _TransfersScreenState extends State<TransfersScreen> {
  final _formKey = GlobalKey<FormState>();
  final _accountController = TextEditingController();
  final _ifscController = TextEditingController();
  final _nameController = TextEditingController();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();

  String? _selectedAccountId;
  bool _isOwnTransfer = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AccountsProvider>().loadAccounts();
    });
  }

  @override
  void dispose() {
    _accountController.dispose();
    _ifscController.dispose();
    _nameController.dispose();
    _amountController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _transfer() async {
    if (!_formKey.currentState!.validate()) return;

    if (_selectedAccountId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select source account')),
      );
      return;
    }

    final accountsProvider = context.read<AccountsProvider>();
    final success = await accountsProvider.transfer(
      fromAccountId: _selectedAccountId!,
      toAccountNumber: _accountController.text.trim(),
      amount: double.parse(_amountController.text.trim()),
      description: _descriptionController.text.trim(),
    );

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Transfer successful!'),
          backgroundColor: ThemeConfig.successColor,
        ),
      );
      _formKey.currentState?.reset();
      _accountController.clear();
      _ifscController.clear();
      _nameController.clear();
      _amountController.clear();
      _descriptionController.clear();
      setState(() => _selectedAccountId = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    final accountsProvider = context.watch<AccountsProvider>();

    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Transfer Money'),
        ),
        body: LoadingOverlay(
          isLoading: accountsProvider.isLoading,
          message: 'Processing transfer...',
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: ThemeConfig.primaryColor.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'From Account',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 8),
                        DropdownButtonFormField<String>(
                          value: _selectedAccountId,
                          decoration: const InputDecoration(
                            prefixIcon: Icon(Icons.account_balance),
                            hintText: 'Select source account',
                            border: OutlineInputBorder(),
                          ),
                          items: accountsProvider.accounts
                              .map((acc) => DropdownMenuItem(
                                    value: acc.id,
                                    child: Text(
                                      '${acc.accountName.isNotEmpty ? acc.accountName : acc.accountType} - ${acc.maskedAccountNumber} (\$${acc.availableBalance.toStringAsFixed(2)})',
                                      style: const TextStyle(fontSize: 13),
                                    ),
                                  ))
                              .toList(),
                          onChanged: (v) =>
                              setState(() => _selectedAccountId = v),
                          validator: (v) =>
                              v == null ? 'Select an account' : null,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: _buildToggleOption(
                          'Own Account',
                          _isOwnTransfer,
                          () => setState(() => _isOwnTransfer = true),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildToggleOption(
                          'Other Bank',
                          !_isOwnTransfer,
                          () => setState(() => _isOwnTransfer = false),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  if (!_isOwnTransfer) ...[
                    TextFormField(
                      controller: _nameController,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Beneficiary Name',
                        prefixIcon: Icon(Icons.person_outline),
                        hintText: 'Enter beneficiary name',
                      ),
                      validator: (v) =>
                          Validators.validateRequired(v, 'Beneficiary name'),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _ifscController,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'IFSC Code',
                        prefixIcon: Icon(Icons.code),
                        hintText: 'Enter IFSC code',
                      ),
                      validator: (v) => Validators.validateIfscCode(v),
                    ),
                    const SizedBox(height: 16),
                  ],
                  TextFormField(
                    controller: _accountController,
                    keyboardType: TextInputType.number,
                    textInputAction: TextInputAction.next,
                    decoration: InputDecoration(
                      labelText: _isOwnTransfer
                          ? 'Account Number'
                          : 'Beneficiary Account Number',
                      prefixIcon: Icon(_isOwnTransfer
                          ? Icons.account_balance
                          : Icons.account_balance_outlined),
                      hintText: _isOwnTransfer
                          ? 'Enter account number'
                          : 'Enter beneficiary account number',
                    ),
                    validator: (v) => Validators.validateAccountNumber(v),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _amountController,
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    textInputAction: TextInputAction.next,
                    decoration: const InputDecoration(
                      labelText: 'Amount',
                      prefixIcon: Icon(Icons.monetization_on_outlined),
                      hintText: '0.00',
                      prefix: Text('\$ '),
                    ),
                    validator: (v) => Validators.validateAmount(v),
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _descriptionController,
                    textInputAction: TextInputAction.done,
                    maxLines: 2,
                    decoration: const InputDecoration(
                      labelText: 'Description (Optional)',
                      prefixIcon: Icon(Icons.description_outlined),
                      hintText: 'What\'s this for?',
                    ),
                  ),
                  if (accountsProvider.error != null) ...[
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: ThemeConfig.errorColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        accountsProvider.error!,
                        style: const TextStyle(
                          color: ThemeConfig.errorColor,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                  const SizedBox(height: 32),
                  AppButton(
                    text: 'Send Money',
                    onPressed: _transfer,
                    isLoading: accountsProvider.isLoading,
                    icon: Icons.send,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildToggleOption(
      String label, bool isSelected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected
              ? ThemeConfig.primaryColor.withOpacity(0.1)
              : ThemeConfig.cardColor,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: isSelected
                ? ThemeConfig.primaryColor
                : ThemeConfig.dividerColor,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              isSelected
                  ? Icons.radio_button_checked
                  : Icons.radio_button_off,
              size: 18,
              color: isSelected
                  ? ThemeConfig.primaryColor
                  : ThemeConfig.textSecondary,
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w500,
                fontSize: 14,
                color: isSelected
                    ? ThemeConfig.primaryColor
                    : ThemeConfig.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
