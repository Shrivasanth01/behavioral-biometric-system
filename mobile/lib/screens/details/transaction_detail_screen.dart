import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/transactions_provider.dart';
import '../../utils/formatters.dart';
import '../../widgets/loading_overlay.dart';
import '../../utils/behavioral_capture.dart';

class TransactionDetailScreen extends StatefulWidget {
  final String transactionId;

  const TransactionDetailScreen({
    super.key,
    required this.transactionId,
  });

  @override
  State<TransactionDetailScreen> createState() =>
      _TransactionDetailScreenState();
}

class _TransactionDetailScreenState extends State<TransactionDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context
          .read<TransactionsProvider>()
          .loadTransactionDetail(widget.transactionId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<TransactionsProvider>();
    final transaction = provider.selectedTransaction;

    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Transaction Details'),
        ),
        body: provider.isLoading && transaction == null
            ? const LoadingIndicator(message: 'Loading details...')
            : transaction == null
                ? const Center(child: Text('Transaction not found'))
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            color: transaction.isCredit
                                ? ThemeConfig.successColor.withOpacity(0.1)
                                : ThemeConfig.errorColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Icon(
                            transaction.isCredit
                                ? Icons.arrow_downward
                                : Icons.arrow_upward,
                            size: 40,
                            color: transaction.isCredit
                                ? ThemeConfig.successColor
                                : ThemeConfig.errorColor,
                          ),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          '${transaction.isCredit ? '+' : '-'}${Formatters.formatCurrency(transaction.amount)}',
                          style: TextStyle(
                            fontSize: 36,
                            fontWeight: FontWeight.bold,
                            color: transaction.isCredit
                                ? ThemeConfig.successColor
                                : ThemeConfig.errorColor,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          transaction.description.isNotEmpty
                              ? transaction.description
                              : transaction.formattedType,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 32),
                        _buildDetailRow(
                          'Status',
                          Formatters.formatStatus(transaction.status),
                          _getStatusColor(transaction.status),
                        ),
                        const Divider(),
                        _buildDetailRow(
                          'Type',
                          transaction.formattedType,
                          null,
                        ),
                        const Divider(),
                        _buildDetailRow(
                          'Reference',
                          transaction.referenceNumber ?? 'N/A',
                          null,
                        ),
                        const Divider(),
                        _buildDetailRow(
                          'Date & Time',
                          Formatters.formatDateTime(transaction.createdAt),
                          null,
                        ),
                        if (transaction.completedAt != null) ...[
                          const Divider(),
                          _buildDetailRow(
                            'Completed',
                            Formatters.formatDateTime(transaction.completedAt!),
                            null,
                          ),
                        ],
                        const Divider(),
                        _buildDetailRow(
                          'Counterparty',
                          transaction.counterpartyName ?? 'N/A',
                          null,
                        ),
                        const Divider(),
                        _buildDetailRow(
                          'Account',
                          transaction.counterpartyAccount ??
                              Formatters.maskAccountNumber(
                                  transaction.accountId),
                          null,
                        ),
                        if (transaction.category != null) ...[
                          const Divider(),
                          _buildDetailRow(
                            'Category',
                            transaction.category!,
                            null,
                          ),
                        ],
                        if (transaction.fee > 0) ...[
                          const Divider(),
                          _buildDetailRow(
                            'Fee',
                            Formatters.formatCurrency(transaction.fee),
                            ThemeConfig.errorColor,
                          ),
                        ],
                        const Divider(),
                        _buildDetailRow(
                          'Balance Before',
                          Formatters.formatCurrency(
                              transaction.balanceBefore),
                          null,
                        ),
                        const Divider(),
                        _buildDetailRow(
                          'Balance After',
                          Formatters.formatCurrency(
                              transaction.balanceAfter),
                          null,
                        ),
                        if (transaction.metadata != null) ...[
                          const SizedBox(height: 20),
                          if (transaction.metadata!.isNotEmpty) ...[
                            const Text(
                              'Additional Details',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 12),
                            ...transaction.metadata!.entries.map(
                              (entry) => Padding(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 4),
                                child: Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      entry.key,
                                      style: const TextStyle(
                                        color: ThemeConfig.textSecondary,
                                      ),
                                    ),
                                    Text(entry.value.toString()),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ],
                      ],
                    ),
                  ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value, Color? valueColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: ThemeConfig.textSecondary,
              fontSize: 14,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.w500,
              fontSize: 14,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'completed':
        return ThemeConfig.successColor;
      case 'pending':
        return ThemeConfig.warningColor;
      case 'failed':
        return ThemeConfig.errorColor;
      case 'reversed':
        return const Color(0xFF9C27B0);
      default:
        return ThemeConfig.textSecondary;
    }
  }
}
