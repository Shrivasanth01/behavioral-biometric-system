import 'package:flutter/material.dart';
import '../config/theme_config.dart';
import '../models/account_model.dart';
import '../utils/formatters.dart';
import 'app_card.dart';

class AccountCard extends StatelessWidget {
  final AccountModel account;
  final VoidCallback? onTap;

  const AccountCard({
    super.key,
    required this.account,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    IconData iconData;
    Color iconColor;

    switch (account.accountType) {
      case 'savings':
        iconData = Icons.savings;
        iconColor = const Color(0xFF4CAF50);
        break;
      case 'current':
        iconData = Icons.account_balance;
        iconColor = const Color(0xFF2196F3);
        break;
      case 'salary':
        iconData = Icons.work;
        iconColor = const Color(0xFFFF9800);
        break;
      case 'fixed_deposit':
        iconData = Icons.lock_clock;
        iconColor = const Color(0xFF9C27B0);
        break;
      default:
        iconData = Icons.account_balance_wallet;
        iconColor = ThemeConfig.primaryColor;
    }

    return AppCard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(
              iconData,
              color: iconColor,
              size: 28,
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
                      account.accountName.isNotEmpty
                          ? account.accountName
                          : Formatters.capitalize(account.accountType),
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: account.isActive
                            ? ThemeConfig.successColor.withOpacity(0.1)
                            : account.isFrozen
                                ? ThemeConfig.warningColor.withOpacity(0.1)
                                : ThemeConfig.errorColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        Formatters.capitalize(account.status),
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w500,
                          color: account.isActive
                              ? ThemeConfig.successColor
                              : account.isFrozen
                                  ? ThemeConfig.warningColor
                                  : ThemeConfig.errorColor,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  account.maskedAccountNumber,
                  style: TextStyle(
                    color: ThemeConfig.textSecondary,
                    fontSize: 13,
                    letterSpacing: 1,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                Formatters.formatCurrency(account.balance),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              if (account.availableBalance != account.balance)
                Text(
                  '${Formatters.formatCurrency(account.availableBalance)} avail',
                  style: TextStyle(
                    color: ThemeConfig.textSecondary,
                    fontSize: 11,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

