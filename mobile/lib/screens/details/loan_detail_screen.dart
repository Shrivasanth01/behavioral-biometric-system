import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../config/theme_config.dart';
import '../../models/loan_model.dart';
import '../../services/banking_service.dart';
import '../../widgets/loading_overlay.dart';
import '../../utils/formatters.dart';
import '../../utils/behavioral_capture.dart';

class LoanDetailScreen extends StatefulWidget {
  final String loanId;

  const LoanDetailScreen({
    super.key,
    required this.loanId,
  });

  @override
  State<LoanDetailScreen> createState() => _LoanDetailScreenState();
}

class _LoanDetailScreenState extends State<LoanDetailScreen> {
  final BankingService _bankingService = BankingService();
  LoanModel? _loan;
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.loanId.isNotEmpty) {
      _loadLoan();
    }
  }

  Future<void> _loadLoan() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      _loan = await _bankingService.getLoanDetail(widget.loanId);
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
          title: const Text('Loan Details'),
        ),
        body: _isLoading
            ? const LoadingIndicator(message: 'Loading loan...')
            : _loan == null
                ? _buildNoLoanView()
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        _buildLoanHeader(),
                        const SizedBox(height: 24),
                        _buildProgressSection(),
                        const SizedBox(height: 24),
                        _buildPaymentSchedule(),
                        const SizedBox(height: 24),
                        _buildLoanInfo(),
                        const SizedBox(height: 24),
                        _buildActionButtons(),
                        const SizedBox(height: 32),
                      ],
                    ),
                  ),
      ),
    );
  }

  Widget _buildNoLoanView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 88,
            height: 88,
            decoration: BoxDecoration(
              color: ThemeConfig.primaryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(22),
            ),
            child: const Icon(
              Icons.account_balance_outlined,
              size: 48,
              color: ThemeConfig.primaryColor,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'No Loan Selected',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Select a loan from the loans screen',
            style: TextStyle(color: ThemeConfig.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildLoanHeader() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF4A148C),
            Color(0xFF6A1B9A),
          ],
        ),
        borderRadius: BorderRadius.circular(ThemeConfig.borderRadius),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    Formatters.capitalize(_loan!.loanType),
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    Formatters.formatCurrency(_loan!.remainingAmount),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  Formatters.formatStatus(_loan!.status),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildHeaderInfo('EMI', _loan!.monthlyEmi),
              _buildHeaderInfo('Tenure', '${_loan!.tenureMonths}m'),
              _buildHeaderInfo('Rate', '${_loan!.interestRate}%'),
              _buildHeaderInfo('Remaining', '${_loan!.remainingMonths}m'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderInfo(String label, dynamic value) {
    return Column(
      children: [
        Text(
          value is double
              ? Formatters.formatCurrency(value)
              : value.toString(),
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white60,
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildProgressSection() {
    final paidPercent = _loan!.progressPercent;
    final remainingPercent = 1.0 - paidPercent;

    return Container(
      padding: const EdgeInsets.all(20),
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
            'Repayment Progress',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 180,
            child: Row(
              children: [
                Expanded(
                  child: PieChart(
                    PieChartData(
                      sections: [
                        PieChartSectionData(
                          value: paidPercent * 100,
                          color: ThemeConfig.successColor,
                          radius: 40,
                          title:
                              '${(paidPercent * 100).toStringAsFixed(0)}%',
                          titleStyle: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        PieChartSectionData(
                          value: remainingPercent * 100,
                          color: Colors.grey.shade300,
                          radius: 35,
                          title:
                              '${(remainingPercent * 100).toStringAsFixed(0)}%',
                          titleStyle: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                      sectionsSpace: 2,
                      centerSpaceRadius: 20,
                    ),
                  ),
                ),
                const SizedBox(width: 20),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildLegend(
                      ThemeConfig.successColor,
                      'Paid',
                      Formatters.formatCurrency(_loan!.amountPaid),
                    ),
                    const SizedBox(height: 12),
                    _buildLegend(
                      Colors.grey.shade300,
                      'Remaining',
                      Formatters.formatCurrency(
                        _loan!.totalPayable - _loan!.amountPaid,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildLegend(
                      ThemeConfig.primaryColor,
                      'Total',
                      Formatters.formatCurrency(_loan!.totalPayable),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLegend(Color color, String label, String value) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(3),
          ),
        ),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 11,
                color: ThemeConfig.textSecondary,
              ),
            ),
            Text(
              value,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildPaymentSchedule() {
    return Container(
      padding: const EdgeInsets.all(20),
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
            'Payment Schedule',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          _buildScheduleRow('Monthly EMI',
              Formatters.formatCurrency(_loan!.monthlyEmi)),
          const Divider(),
          _buildScheduleRow(
            'Next Payment',
            _loan!.nextPaymentDate != null
                ? Formatters.formatDate(_loan!.nextPaymentDate!)
                : 'N/A',
          ),
          const Divider(),
          _buildScheduleRow('Total Payable',
              Formatters.formatCurrency(_loan!.totalPayable)),
          const Divider(),
          _buildScheduleRow('Total Interest',
              Formatters.formatCurrency(_loan!.totalInterest)),
          if (_loan!.lateFee != null) ...[
            const Divider(),
            _buildScheduleRow(
              'Late Fee',
              Formatters.formatCurrency(_loan!.lateFee!),
              valueColor: ThemeConfig.errorColor,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildScheduleRow(
    String label,
    String value, {
    Color? valueColor,
  }) {
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
            style: TextStyle(
              fontWeight: FontWeight.w600,
              fontSize: 14,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoanInfo() {
    return Container(
      padding: const EdgeInsets.all(20),
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
            'Loan Information',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          _buildInfoRow('Loan Type',
              Formatters.capitalize(_loan!.loanType)),
          const Divider(),
          _buildInfoRow(
              'Principal', Formatters.formatCurrency(_loan!.principalAmount)),
          const Divider(),
          _buildInfoRow(
              'Interest Rate', '${_loan!.interestRate}% per annum'),
          const Divider(),
          _buildInfoRow('Tenure', '${_loan!.tenureMonths} months'),
          if (_loan!.purpose != null) ...[
            const Divider(),
            _buildInfoRow('Purpose', _loan!.purpose!),
          ],
          const Divider(),
          _buildInfoRow(
              'Applied', Formatters.formatDate(_loan!.createdAt)),
          if (_loan!.approvedAt != null) ...[
            const Divider(),
            _buildInfoRow(
                'Approved', Formatters.formatDate(_loan!.approvedAt!)),
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
          Text(label,
              style: const TextStyle(
                  color: ThemeConfig.textSecondary, fontSize: 14)),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                  fontWeight: FontWeight.w500, fontSize: 14),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.payment),
            label: const Text('Pay EMI Now'),
            style: ElevatedButton.styleFrom(
              backgroundColor: ThemeConfig.primaryColor,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.calculate),
            label: const Text('Calculate EMI'),
            style: OutlinedButton.styleFrom(
              foregroundColor: ThemeConfig.primaryColor,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
