import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../config/theme_config.dart';
import '../../providers/accounts_provider.dart';
import '../../providers/transactions_provider.dart';
import '../../providers/behavioral_provider.dart';
import '../../models/transaction_model.dart';
import '../../utils/formatters.dart';
import '../../widgets/balance_card.dart';
import '../../widgets/transaction_tile.dart';
import '../../widgets/behavioral_indicator.dart';
import '../../widgets/empty_state.dart';
import '../../utils/behavioral_capture.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AccountsProvider>().loadAccounts();
      context.read<AccountsProvider>().loadRecentTransactions();
      context.read<BehavioralProvider>().loadProfile();
    });
  }

  @override
  Widget build(BuildContext context) {
    final accountsProvider = context.watch<AccountsProvider>();
    final behavioralProvider = context.watch<BehavioralProvider>();

    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('SecureBank'),
          actions: [
            IconButton(
              icon: const Icon(Icons.notifications_outlined),
              onPressed: () {},
            ),
            IconButton(
              icon: const Icon(Icons.qr_code_scanner),
              onPressed: () {
                Navigator.pushNamed(context, '/transfers');
              },
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: () async {
            await accountsProvider.loadAccounts();
            await accountsProvider.loadRecentTransactions();
            await behavioralProvider.loadProfile();
          },
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (accountsProvider.isLoading &&
                    accountsProvider.accounts.isEmpty)
                  const SizedBox(
                    height: 200,
                    child: Center(child: CircularProgressIndicator()),
                  )
                else
                  BalanceCard(
                    balance: accountsProvider.totalBalance,
                    availableBalance: accountsProvider.totalAvailableBalance,
                    onTap: () {
                      if (accountsProvider.accounts.isNotEmpty) {
                        Navigator.pushNamed(
                          context,
                          '/account-detail',
                          arguments: accountsProvider.accounts.first.id,
                        );
                      }
                    },
                  ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    Expanded(
                      child: _buildQuickActionCard(
                        icon: Icons.send_money,
                        label: 'Transfer',
                        color: const Color(0xFF2196F3),
                        onTap: () =>
                            Navigator.pushNamed(context, '/transfers'),
                      ),
                    ),
                    Expanded(
                      child: _buildQuickActionCard(
                        icon: Icons.payment,
                        label: 'Payments',
                        color: const Color(0xFF4CAF50),
                        onTap: () =>
                            Navigator.pushNamed(context, '/beneficiaries'),
                      ),
                    ),
                    Expanded(
                      child: _buildQuickActionCard(
                        icon: Icons.credit_card,
                        label: 'Cards',
                        color: const Color(0xFFFF9800),
                        onTap: () => Navigator.pushNamed(
                            context, '/card-detail',
                            arguments: ''),
                      ),
                    ),
                    Expanded(
                      child: _buildQuickActionCard(
                        icon: Icons.account_balance,
                        label: 'Loans',
                        color: const Color(0xFF9C27B0),
                        onTap: () => Navigator.pushNamed(
                            context, '/loan-detail',
                            arguments: ''),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                if (behavioralProvider.isCollecting) ...[
                  BehavioralTrustBar(
                    trustScore: behavioralProvider.trustScore,
                  ),
                  const SizedBox(height: 20),
                ],
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Recent Transactions',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    TextButton(
                      onPressed: () =>
                          Navigator.pushNamed(context, '/accounts'),
                      child: const Text('View All'),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                if (accountsProvider.recentTransactions.isEmpty &&
                    !accountsProvider.isLoading)
                  const EmptyState(
                    icon: Icons.receipt_long_outlined,
                    title: 'No transactions yet',
                    subtitle: 'Your recent transactions will appear here',
                  )
                else
                  ...accountsProvider.recentTransactions.map(
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
                const SizedBox(height: 16),
                _buildSpendingChart(),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _buildStatCard(
                      'Total Debits',
                      Formatters.formatCurrency(
                          accountsProvider.recentTransactions
                              .where((t) => t.isDebit)
                              .fold(0.0, (s, t) => s + t.amount)),
                      Icons.arrow_upward,
                      ThemeConfig.errorColor,
                    ),
                    const SizedBox(width: 12),
                    _buildStatCard(
                      'Total Credits',
                      Formatters.formatCurrency(
                          accountsProvider.recentTransactions
                              .where((t) => t.isCredit)
                              .fold(0.0, (s, t) => s + t.amount)),
                      Icons.arrow_downward,
                      ThemeConfig.successColor,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionCard({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
        decoration: BoxDecoration(
          color: ThemeConfig.cardColor,
          borderRadius: BorderRadius.circular(12),
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
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(
      String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: ThemeConfig.cardColor,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 18),
                const SizedBox(width: 6),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    color: ThemeConfig.textSecondary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSpendingChart() {
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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Spending Overview',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 150,
            child: BarChart(
              BarChartData(
                alignment: BarChartAlignment.spaceAround,
                maxY: 1000,
                barTouchData: BarTouchData(enabled: false),
                titlesData: FlTitlesData(
                  show: true,
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                        if (value.toInt() >= 0 && value.toInt() < days.length) {
                          return Text(
                            days[value.toInt()],
                            style: const TextStyle(fontSize: 10),
                          );
                        }
                        return const Text('');
                      },
                    ),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  topTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  rightTitles: AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                ),
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: 250,
                  getDrawingHorizontalLine: (value) {
                    return FlLine(
                      color: ThemeConfig.dividerColor,
                      strokeWidth: 1,
                    );
                  },
                ),
                borderData: FlBorderData(show: false),
                barGroups: [
                  _makeBarGroup(0, 400),
                  _makeBarGroup(1, 650),
                  _makeBarGroup(2, 300),
                  _makeBarGroup(3, 800),
                  _makeBarGroup(4, 500),
                  _makeBarGroup(5, 750),
                  _makeBarGroup(6, 600),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  BarChartGroupData _makeBarGroup(int x, double y) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: y,
          color: ThemeConfig.primaryColor,
          width: 16,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(4),
            topRight: Radius.circular(4),
          ),
        ),
      ],
    );
  }
}
