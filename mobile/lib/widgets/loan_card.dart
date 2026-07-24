import 'package:flutter/material.dart';
import '../config/theme_config.dart';
import '../models/loan_model.dart';
import '../utils/formatters.dart';
import 'app_card.dart';

class LoanCard extends StatelessWidget {
  final LoanModel loan;
  final VoidCallback? onTap;

  const LoanCard({
    super.key,
    required this.loan,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return AppCard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: _getLoanColor().withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      _getLoanIcon(),
                      color: _getLoanColor(),
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        Formatters.capitalize(loan.loanType),
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${loan.remainingMonths} months remaining',
                        style: TextStyle(
                          color: ThemeConfig.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: _getStatusColor().withOpacity(0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  Formatters.capitalize(loan.status),
                  style: TextStyle(
                    color: _getStatusColor(),
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildInfoColumn('Principal', loan.principalAmount),
              _buildInfoColumn('Remaining', loan.remainingAmount),
              _buildInfoColumn('EMI', loan.monthlyEmi),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: loan.progressPercent,
              backgroundColor: Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(_getLoanColor()),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${(loan.progressPercent * 100).toStringAsFixed(0)}% paid',
                style: TextStyle(
                  color: ThemeConfig.textSecondary,
                  fontSize: 11,
                ),
              ),
              Text(
                '${Formatters.formatCurrency(loan.amountPaid)} / ${Formatters.formatCurrency(loan.totalPayable)}',
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

  Widget _buildInfoColumn(String label, double amount) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: ThemeConfig.textSecondary,
            fontSize: 11,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          Formatters.formatCurrency(amount),
          style: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 14,
          ),
        ),
      ],
    );
  }

  Color _getLoanColor() {
    switch (loan.loanType) {
      case 'personal':
        return const Color(0xFF2196F3);
      case 'home':
        return const Color(0xFF4CAF50);
      case 'car':
        return const Color(0xFFFF9800);
      case 'education':
        return const Color(0xFF9C27B0);
      case 'business':
        return const Color(0xFF795548);
      case 'gold':
        return const Color(0xFFFFD600);
      default:
        return ThemeConfig.primaryColor;
    }
  }

  IconData _getLoanIcon() {
    switch (loan.loanType) {
      case 'personal':
        return Icons.person;
      case 'home':
        return Icons.home;
      case 'car':
        return Icons.directions_car;
      case 'education':
        return Icons.school;
      case 'business':
        return Icons.business;
      case 'gold':
        return Icons.monetization_on;
      default:
        return Icons.account_balance;
    }
  }

  Color _getStatusColor() {
    switch (loan.status) {
      case 'active':
        return ThemeConfig.successColor;
      case 'pending':
        return ThemeConfig.warningColor;
      case 'approved':
        return const Color(0xFF2196F3);
      case 'closed':
        return ThemeConfig.textSecondary;
      case 'defaulted':
        return ThemeConfig.errorColor;
      default:
        return ThemeConfig.textSecondary;
    }
  }
}

