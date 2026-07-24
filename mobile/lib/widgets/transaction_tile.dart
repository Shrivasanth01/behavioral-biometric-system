import 'package:flutter/material.dart';
import '../config/theme_config.dart';
import '../models/transaction_model.dart';
import '../utils/formatters.dart';

class TransactionTile extends StatelessWidget {
  final TransactionModel transaction;
  final VoidCallback? onTap;

  const TransactionTile({
    super.key,
    required this.transaction,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isCredit = transaction.isCredit;
    final amountColor = isCredit ? ThemeConfig.successColor : ThemeConfig.errorColor;
    final amountPrefix = isCredit ? '+' : '-';

    IconData iconData;
    Color iconColor;

    switch (transaction.type) {
      case 'deposit':
        iconData = Icons.arrow_downward;
        iconColor = ThemeConfig.successColor;
        break;
      case 'withdrawal':
        iconData = Icons.arrow_upward;
        iconColor = ThemeConfig.errorColor;
        break;
      case 'transfer':
        iconData = Icons.send;
        iconColor = ThemeConfig.primaryColor;
        break;
      case 'payment':
        iconData = Icons.payment;
        iconColor = ThemeConfig.warningColor;
        break;
      case 'refund':
        iconData = Icons.replay;
        iconColor = ThemeConfig.successColor;
        break;
      case 'interest':
        iconData = Icons.trending_up;
        iconColor = ThemeConfig.successColor;
        break;
      case 'fee':
        iconData = Icons.money_off;
        iconColor = ThemeConfig.errorColor;
        break;
      default:
        iconData = Icons.receipt_long;
        iconColor = ThemeConfig.textSecondary;
    }

    return ListTile(
      onTap: onTap,
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: iconColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          iconData,
          color: iconColor,
          size: 22,
        ),
      ),
      title: Text(
        transaction.description.isNotEmpty
            ? transaction.description
            : transaction.formattedType,
        style: const TextStyle(
          fontWeight: FontWeight.w500,
          fontSize: 15,
        ),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      subtitle: Text(
        Formatters.formatDateTime(transaction.createdAt),
        style: TextStyle(
          color: ThemeConfig.textSecondary,
          fontSize: 12,
        ),
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            '$amountPrefix${Formatters.formatCurrency(transaction.amount)}',
            style: TextStyle(
              color: amountColor,
              fontWeight: FontWeight.w600,
              fontSize: 15,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            Formatters.formatStatus(transaction.status),
            style: TextStyle(
              color: transaction.isPending
                  ? ThemeConfig.warningColor
                  : transaction.isCompleted
                      ? ThemeConfig.successColor
                      : ThemeConfig.errorColor,
              fontSize: 11,
            ),
          ),
        ],
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 4,
      ),
    );
  }
}
