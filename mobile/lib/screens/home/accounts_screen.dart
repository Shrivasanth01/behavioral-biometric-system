import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/accounts_provider.dart';
import '../../models/account_model.dart';
import '../../widgets/account_card.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/empty_state.dart';
import '../../utils/behavioral_capture.dart';

class AccountsScreen extends StatefulWidget {
  const AccountsScreen({super.key});

  @override
  State<AccountsScreen> createState() => _AccountsScreenState();
}

class _AccountsScreenState extends State<AccountsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AccountsProvider>().loadAccounts();
    });
  }

  @override
  Widget build(BuildContext context) {
    final accountsProvider = context.watch<AccountsProvider>();

    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('My Accounts'),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => accountsProvider.loadAccounts(),
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: () => accountsProvider.loadAccounts(),
          child: accountsProvider.isLoading && accountsProvider.accounts.isEmpty
              ? const LoadingIndicator(message: 'Loading accounts...')
              : accountsProvider.accounts.isEmpty
                  ? const EmptyState(
                      icon: Icons.account_balance_outlined,
                      title: 'No accounts yet',
                      subtitle: 'You don\'t have any accounts',
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: accountsProvider.accounts.length + 1,
                      itemBuilder: (context, index) {
                        if (index == 0) {
                          return _buildAccountSummary(accountsProvider);
                        }
                        final account =
                            accountsProvider.accounts[index - 1];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: AccountCard(
                            account: account,
                            onTap: () {
                              Navigator.pushNamed(
                                context,
                                '/account-detail',
                                arguments: account.id,
                              );
                            },
                          ),
                        );
                      },
                    ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {},
          child: const Icon(Icons.add),
        ),
      ),
    );
  }

  Widget _buildAccountSummary(AccountsProvider provider) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF1A237E),
            Color(0xFF283593),
          ],
        ),
        borderRadius: BorderRadius.circular(ThemeConfig.borderRadius),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Total Balance',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '$ ${provider.totalBalance.toStringAsFixed(2)}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 36,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  '${provider.activeAccounts.length} active account${provider.activeAccounts.length != 1 ? 's' : ''}',
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
