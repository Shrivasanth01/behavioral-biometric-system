import 'package:flutter/material.dart';
import '../../config/theme_config.dart';
import '../../models/beneficiary_model.dart';
import '../../services/banking_service.dart';
import '../../widgets/app_button.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/empty_state.dart';
import '../../utils/behavioral_capture.dart';

class BeneficiaryScreen extends StatefulWidget {
  const BeneficiaryScreen({super.key});

  @override
  State<BeneficiaryScreen> createState() => _BeneficiaryScreenState();
}

class _BeneficiaryScreenState extends State<BeneficiaryScreen> {
  final BankingService _bankingService = BankingService();
  List<BeneficiaryModel> _beneficiaries = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadBeneficiaries();
  }

  Future<void> _loadBeneficiaries() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      _beneficiaries = await _bankingService.getBeneficiaries();
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
          title: const Text('Beneficiaries'),
          actions: [
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: () => _showAddBeneficiaryDialog(),
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: _loadBeneficiaries,
          child: _isLoading && _beneficiaries.isEmpty
              ? const LoadingIndicator(message: 'Loading beneficiaries...')
              : _beneficiaries.isEmpty
                  ? const EmptyState(
                      icon: Icons.people_outline,
                      title: 'No beneficiaries',
                      subtitle:
                          'Add beneficiaries for quick transfers',
                      actionLabel: 'Add Beneficiary',
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _beneficiaries.length,
                      itemBuilder: (context, index) {
                        final beneficiary = _beneficiaries[index];
                        return _buildBeneficiaryCard(beneficiary);
                      },
                    ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => _showAddBeneficiaryDialog(),
          child: const Icon(Icons.add),
        ),
      ),
    );
  }

  Widget _buildBeneficiaryCard(BeneficiaryModel beneficiary) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: ThemeConfig.cardColor,
        borderRadius: BorderRadius.circular(ThemeConfig.borderRadius),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: ThemeConfig.primaryColor.withOpacity(0.1),
            child: Text(
              beneficiary.displayName.isNotEmpty
                  ? beneficiary.displayName[0].toUpperCase()
                  : '?',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: ThemeConfig.primaryColor,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      beneficiary.displayName,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                    if (beneficiary.isFavorite)
                      const Padding(
                        padding: EdgeInsets.only(left: 6),
                        child: Icon(
                          Icons.star,
                          size: 16,
                          color: Color(0xFFFFD600),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  beneficiary.bankName.isNotEmpty
                      ? '${beneficiary.bankName} - ${beneficiary.maskedAccount}'
                      : beneficiary.maskedAccount,
                  style: const TextStyle(
                    color: ThemeConfig.textSecondary,
                    fontSize: 13,
                  ),
                ),
                if (beneficiary.lastTransfer != null)
                  Text(
                    'Last transfer: ${_formatDate(beneficiary.lastTransfer!)}',
                    style: const TextStyle(
                      color: ThemeConfig.textHint,
                      fontSize: 11,
                    ),
                  ),
              ],
            ),
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'edit':
                  _showEditBeneficiaryDialog(beneficiary);
                  break;
                case 'delete':
                  _confirmDelete(beneficiary);
                  break;
                case 'transfer':
                  Navigator.pushNamed(context, '/transfers');
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'transfer',
                child: Row(
                  children: [
                    Icon(Icons.send, size: 18),
                    SizedBox(width: 8),
                    Text('Transfer'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'edit',
                child: Row(
                  children: [
                    Icon(Icons.edit, size: 18),
                    SizedBox(width: 8),
                    Text('Edit'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete, size: 18, color: ThemeConfig.errorColor),
                    SizedBox(width: 8),
                    Text('Delete', style: TextStyle(color: ThemeConfig.errorColor)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    if (diff.inDays < 1) return 'Today';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${date.month}/${date.day}/${date.year}';
  }

  void _showAddBeneficiaryDialog() {
    _showBeneficiaryForm();
  }

  void _showEditBeneficiaryDialog(BeneficiaryModel beneficiary) {
    _showBeneficiaryForm(beneficiary: beneficiary);
  }

  void _showBeneficiaryForm({BeneficiaryModel? beneficiary}) {
    final formKey = GlobalKey<FormState>();
    final nameController =
        TextEditingController(text: beneficiary?.name ?? '');
    final accountController =
        TextEditingController(text: beneficiary?.accountNumber ?? '');
    final bankController =
        TextEditingController(text: beneficiary?.bankName ?? '');
    final nicknameController =
        TextEditingController(text: beneficiary?.nickname ?? '');
    final phoneController =
        TextEditingController(text: beneficiary?.phone ?? '');

    final isEditing = beneficiary != null;

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
                Text(
                  isEditing ? 'Edit Beneficiary' : 'Add Beneficiary',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: nameController,
                  textInputAction: TextInputAction.next,
                  decoration: const InputDecoration(
                    labelText: 'Full Name',
                    prefixIcon: Icon(Icons.person),
                  ),
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: accountController,
                  textInputAction: TextInputAction.next,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Account Number',
                    prefixIcon: Icon(Icons.account_balance),
                  ),
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: bankController,
                  textInputAction: TextInputAction.next,
                  decoration: const InputDecoration(
                    labelText: 'Bank Name',
                    prefixIcon: Icon(Icons.business),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: nicknameController,
                  textInputAction: TextInputAction.next,
                  decoration: const InputDecoration(
                    labelText: 'Nickname (Optional)',
                    prefixIcon: Icon(Icons.label),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: phoneController,
                  textInputAction: TextInputAction.done,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'Phone (Optional)',
                    prefixIcon: Icon(Icons.phone),
                  ),
                ),
                const SizedBox(height: 24),
                AppButton(
                  text: isEditing ? 'Update' : 'Add Beneficiary',
                  onPressed: () {
                    if (formKey.currentState!.validate()) {
                      Navigator.pop(ctx);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            isEditing
                                ? 'Beneficiary updated'
                                : 'Beneficiary added',
                          ),
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

  void _confirmDelete(BeneficiaryModel beneficiary) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Beneficiary'),
        content: Text(
          'Are you sure you want to remove ${beneficiary.displayName} from your beneficiaries?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              _bankingService.deleteBeneficiary(beneficiary.id);
              _loadBeneficiaries();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Beneficiary deleted'),
                  backgroundColor: ThemeConfig.successColor,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: ThemeConfig.errorColor,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}
