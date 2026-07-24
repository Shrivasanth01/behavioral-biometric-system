import 'dart:math';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../config/theme_config.dart';
import '../../widgets/app_button.dart';
import '../../utils/formatters.dart';
import '../../utils/behavioral_capture.dart';

class EmiCalculatorScreen extends StatefulWidget {
  const EmiCalculatorScreen({super.key});

  @override
  State<EmiCalculatorScreen> createState() => _EmiCalculatorScreenState();
}

class _EmiCalculatorScreenState extends State<EmiCalculatorScreen> {
  final _amountController = TextEditingController(text: '100000');
  final _rateController = TextEditingController(text: '10.99');
  final _tenureController = TextEditingController(text: '12');

  double _emi = 0;
  double _totalInterest = 0;
  double _totalPayable = 0;
  bool _calculated = false;

  @override
  void dispose() {
    _amountController.dispose();
    _rateController.dispose();
    _tenureController.dispose();
    super.dispose();
  }

  void _calculateEmi() {
    final principal = double.tryParse(_amountController.text) ?? 0;
    final rate = double.tryParse(_rateController.text) ?? 0;
    final tenure = int.tryParse(_tenureController.text) ?? 0;

    if (principal <= 0 || rate <= 0 || tenure <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter valid values')),
      );
      return;
    }

    final monthlyRate = rate / (12 * 100);
    final emi = principal *
        monthlyRate *
        pow(1 + monthlyRate, tenure) /
        (pow(1 + monthlyRate, tenure) - 1);

    _emi = emi;
    _totalPayable = emi * tenure;
    _totalInterest = _totalPayable - principal;

    setState(() => _calculated = true);
  }

  @override
  Widget build(BuildContext context) {
    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('EMI Calculator'),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: ThemeConfig.cardColor,
                  borderRadius:
                      BorderRadius.circular(ThemeConfig.borderRadius),
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
                      'Loan Details',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 20),
                    TextFormField(
                      controller: _amountController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Loan Amount',
                        prefixIcon: Icon(Icons.monetization_on),
                        prefix: Text('\$ '),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _rateController,
                      keyboardType:
                          const TextInputType.numberWithOptions(
                              decimal: true),
                      decoration: const InputDecoration(
                        labelText: 'Interest Rate (% per annum)',
                        prefixIcon: Icon(Icons.trending_up),
                        suffix: Text('%'),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _tenureController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Tenure (Months)',
                        prefixIcon: Icon(Icons.calendar_today),
                        suffix: Text('months'),
                      ),
                    ),
                    const SizedBox(height: 24),
                    AppButton(
                      text: 'Calculate EMI',
                      onPressed: _calculateEmi,
                      icon: Icons.calculate,
                    ),
                  ],
                ),
              ),
              if (_calculated) ...[
                const SizedBox(height: 24),
                _buildResultCard(),
                const SizedBox(height: 20),
                _buildChart(),
                const SizedBox(height: 20),
                _buildAmortizationTable(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResultCard() {
    final principal = double.parse(_amountController.text);

    return Container(
      padding: const EdgeInsets.all(24),
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
        children: [
          const Text(
            'Monthly EMI',
            style: TextStyle(color: Colors.white70, fontSize: 14),
          ),
          const SizedBox(height: 8),
          Text(
            Formatters.formatCurrency(_emi),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 36,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildResultItem(
                'Principal',
                Formatters.formatCurrency(principal),
              ),
              _buildResultItem(
                'Interest',
                Formatters.formatCurrency(_totalInterest),
              ),
              _buildResultItem(
                'Total',
                Formatters.formatCurrency(_totalPayable),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildResultItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white60,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildChart() {
    final principal = double.parse(_amountController.text);
    final principalPercent = (principal / _totalPayable) * 100;
    final interestPercent = (_totalInterest / _totalPayable) * 100;

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
            'Breakdown',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 160,
            child: Row(
              children: [
                Expanded(
                  child: PieChart(
                    PieChartData(
                      sections: [
                        PieChartSectionData(
                          value: principalPercent,
                          color: ThemeConfig.primaryColor,
                          radius: 45,
                          title:
                              '${principalPercent.toStringAsFixed(0)}%',
                          titleStyle: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        PieChartSectionData(
                          value: interestPercent,
                          color: ThemeConfig.accentColor,
                          radius: 40,
                          title:
                              '${interestPercent.toStringAsFixed(0)}%',
                          titleStyle: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ],
                      sectionsSpace: 2,
                      centerSpaceRadius: 25,
                    ),
                  ),
                ),
                const SizedBox(width: 20),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildChartLegend(
                      ThemeConfig.primaryColor,
                      'Principal',
                      Formatters.formatCurrency(principal),
                    ),
                    const SizedBox(height: 12),
                    _buildChartLegend(
                      ThemeConfig.accentColor,
                      'Interest',
                      Formatters.formatCurrency(_totalInterest),
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

  Widget _buildChartLegend(
      Color color, String label, String value) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(3),
          ),
        ),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label,
                style: const TextStyle(
                    fontSize: 11,
                    color: ThemeConfig.textSecondary)),
            Text(value,
                style: const TextStyle(
                    fontSize: 13, fontWeight: FontWeight.w600)),
          ],
        ),
      ],
    );
  }

  Widget _buildAmortizationTable() {
    final principal = double.parse(_amountController.text);
    final rate = double.parse(_rateController.text);
    final tenure = int.parse(_tenureController.text);
    final monthlyRate = rate / (12 * 100);

    double balance = principal;
    final rows = <Map<String, double>>[];

    for (int i = 1; i <= min(tenure, 12); i++) {
      final interest = balance * monthlyRate;
      final principalPaid = _emi - interest;
      balance -= principalPaid;

      rows.add({
        'month': i.toDouble(),
        'emi': _emi,
        'principal': principalPaid,
        'interest': interest,
        'balance': balance < 0 ? 0 : balance,
      });
    }

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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Payment Schedule',
                style: TextStyle(
                    fontSize: 16, fontWeight: FontWeight.bold),
              ),
              Text(
                'First ${rows.length} months',
                style: const TextStyle(
                    fontSize: 12,
                    color: ThemeConfig.textSecondary),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columnSpacing: 20,
              columns: const [
                DataColumn(label: Text('Month',
                    style: TextStyle(fontWeight: FontWeight.bold))),
                DataColumn(label: Text('EMI',
                    style: TextStyle(fontWeight: FontWeight.bold))),
                DataColumn(label: Text('Principal',
                    style: TextStyle(fontWeight: FontWeight.bold))),
                DataColumn(label: Text('Interest',
                    style: TextStyle(fontWeight: FontWeight.bold))),
                DataColumn(label: Text('Balance',
                    style: TextStyle(fontWeight: FontWeight.bold))),
              ],
              rows: rows.map((row) {
                return DataRow(cells: [
                  DataCell(Text('#${row['month']!.toInt()}')),
                  DataCell(Text(Formatters
                      .formatCurrency(row['emi']!)
                      .replaceAll('\$', ''))),
                  DataCell(Text(Formatters
                      .formatCurrency(row['principal']!)
                      .replaceAll('\$', ''))),
                  DataCell(Text(Formatters
                      .formatCurrency(row['interest']!)
                      .replaceAll('\$', ''))),
                  DataCell(Text(Formatters
                      .formatCurrency(row['balance']!)
                      .replaceAll('\$', ''))),
                ]);
              }).toList(),
            ),
          ),
          if (tenure > 12)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(
                '+${tenure - 12} more months',
                style: const TextStyle(
                  color: ThemeConfig.textSecondary,
                  fontSize: 13,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
