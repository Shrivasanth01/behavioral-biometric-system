import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/accounts_provider.dart';
import '../../providers/transactions_provider.dart';
import '../../models/account_model.dart';
import '../../widgets/balance_card.dart';
import '../../widgets/transaction_tile.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/empty_state.dart';
import '../../utils/formatters.dart';
import '../../utils/behavioral_capture.dart';

class AccountDetailScreen extends StatefulWidget {
  final String accountId;

  const AccountDetailScreen({
    super.key,
    required this.accountId,
  });

  @override
  State<AccountDetailScreen> createState() => _AccountDetailScreenState();
}

class _AccountDetailScreenState extends State<AccountDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context
          .read<AccountsProvider>()
          .loadAccountDetail(widget.accountId);
      context
          .read<TransactionsProvider>()
          .setAccountFilter(widget.accountId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final accountsProvider = context.watch<AccountsProvider>();
    final transactionsProvider = context.watch<TransactionsProvider>();
    final account = accountsProvider.selectedAccount;

    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            account?.accountName.isNotEmpty == true
                ? account!.accountName
                : 'Account Details',
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.more_vert),
              onPressed: () {},
            ),
          ],
        ),
        body: accountsProvider.isLoading && account == null
            ? const LoadingIndicator(message: 'Loading account...')
            : account == null
                ? const Center(child: Text('Account not found'))
                : RefreshIndicator(
                    onRefresh: () async {
                      await accountsProvider
                          .loadAccountDetail(widget.accountId);
                      await transactionsProvider
                          .setAccountFilter(widget.accountId);
                    },
                    child: SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          BalanceCard(
                            balance: account.balance,
                            availableBalance: account.availableBalance,
                            accountName: account.accountName.isNotEmpty
                                ? account.accountName
                                : Formatters.capitalize(
                                    account.accountType),
                            accountNumber: account.accountNumber,
                            maskedNumber: account.maskedAccountNumber,
                          ),
                          const SizedBox(height: 24),
                          _buildAccountInfo(account),
                          const SizedBox(height: 24),
                          Row(
                            mainAxisAlignment:
                                MainAxisAlignment.spaceBetween,
                            children: [
                              _buildActionButton(
                                icon: Icons.send_money,
                                label: 'Transfer',
                                onTap: () {
                                  Navigator.pushNamed(
                                      context, '/transfers');
                                },
                              ),
                              _buildActionButton(
                                icon: Icons.payment,
                                label: 'Pay',
                                onTap: () {},
                              ),
                              _buildActionButton(
                                icon: Icons.download,
                                label: 'Statement',
                                onTap: () {},
                              ),
                              _buildActionButton(
                                icon: Icons.share,
                                label: 'Share',
                                onTap: () {},
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),
                          Row(
                            mainAxisAlignment:
                                MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Transactions',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              TextButton(
                                onPressed: () {},
                                child: const Text('Filter'),
                              ),
                            ],
                          ),
                          if (transactionsProvider.transactions.isEmpty)
                            const EmptyState(
                              icon: Icons.receipt_long_outlined,
                              title: 'No transactions',
                              subtitle:
                                  'Transactions will appear here',
                            )
                          else
                            ...transactionsProvider.transactions.map(
                              (t) => TransactionTile(
                                transaction: t,
                                onTap: () {
                                  Navigator.pushNamed(
                                    context,
                                    '/transaction-detail',
                                    arguments: t.id,
                                  );
                                },
                              ),
                            ),
                          if (transactionsProvider.hasMore)
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(vertical: 16),
                              child: Center(
                                child: TextButton(
                                  onPressed: () => transactionsProvider
                                      .loadTransactions(),
                                  child: transactionsProvider.isLoading
                                      ? const SizedBox(
                                          width: 20,
                                          height: 20,
                                          child:
                                              CircularProgressIndicator(
                                            strokeWidth: 2,
                                          ),
                                        )
                                      : const Text('Load More'),
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
      ),
    );
  }

  Widget _buildAccountInfo(AccountModel account) {
    return Container(
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
      child: Column(
        children: [
          _buildInfoRow('Account Type',
              Formatters.capitalize(account.accountType)),
          const Divider(),
          _buildInfoRow(
              'Account Number',
              Formatters.formatAccountNumber(
                  account.accountNumber)),
          const Divider(),
          _buildInfoRow('Status',
              Formatters.formatStatus(account.status)),
          const Divider(),
          _buildInfoRow(
            'Created',
            Formatters.formatDate(account.createdAt),
          ),
          if (account.lastTransaction != null) ...[
            const Divider(),
            _buildInfoRow(
              'Last Transaction',
              Formatters.formatDate(account.lastTransaction!),
            ),
          ],
          if (account.features.isNotEmpty) ...[
            const Divider(),
            _buildInfoRow('Features', account.features.join(', ')),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
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
            style: const TextStyle(
              fontWeight: FontWeight.w500,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 72,
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: ThemeConfig.cardColor,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Icon(icon, color: ThemeConfig.primaryColor, size: 24),
            const SizedBox(height: 6),
            Text(
              label,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
