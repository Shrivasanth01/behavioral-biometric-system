import 'package:flutter/material.dart';
import '../../config/theme_config.dart';
import '../../models/card_model.dart';
import '../../services/banking_service.dart';
import '../../widgets/card_widget.dart';
import '../../widgets/app_button.dart';
import '../../widgets/loading_overlay.dart';
import '../../utils/formatters.dart';
import '../../utils/behavioral_capture.dart';

class CardDetailScreen extends StatefulWidget {
  final String cardId;

  const CardDetailScreen({
    super.key,
    required this.cardId,
  });

  @override
  State<CardDetailScreen> createState() => _CardDetailScreenState();
}

class _CardDetailScreenState extends State<CardDetailScreen> {
  final BankingService _bankingService = BankingService();
  CardModel? _card;
  bool _isLoading = false;
  bool _showDetails = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.cardId.isNotEmpty) {
      _loadCard();
    }
  }

  Future<void> _loadCard() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      _card = await _bankingService.getCardDetail(widget.cardId);
    } catch (e) {
      _error = e.toString();
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleCardStatus() async {
    if (_card == null) return;

    final newStatus = _card!.isActive ? 'blocked' : 'active';
    try {
      final updated = await _bankingService.updateCardStatus(
        widget.cardId,
        newStatus,
      );
      if (mounted) setState(() => _card = updated);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Card Details'),
          actions: [
            PopupMenuButton<String>(
              onSelected: (value) {
                switch (value) {
                  case 'block':
                    _toggleCardStatus();
                    break;
                  case 'pin':
                    _showChangePinDialog();
                    break;
                  case 'report':
                    break;
                }
              },
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'block',
                  child: Text('Block / Unblock'),
                ),
                const PopupMenuItem(
                  value: 'pin',
                  child: Text('Change PIN'),
                ),
                const PopupMenuItem(
                  value: 'report',
                  child: Text('Report Lost'),
                ),
              ],
            ),
          ],
        ),
        body: _isLoading
            ? const LoadingIndicator(message: 'Loading card...')
            : _card == null
                ? _buildNoCardView()
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        CardWidget(
                          card: _card!,
                          showFullDetails: _showDetails,
                        ),
                        const SizedBox(height: 16),
                        TextButton.icon(
                          onPressed: () =>
                              setState(() => _showDetails = !_showDetails),
                          icon: Icon(
                            _showDetails
                                ? Icons.visibility_off
                                : Icons.visibility,
                            size: 18,
                          ),
                          label: Text(
                            _showDetails
                                ? 'Hide Details'
                                : 'Show Card Details',
                          ),
                        ),
                        const SizedBox(height: 24),
                        _buildCardInfo(),
                        const SizedBox(height: 24),
                        Row(
                          children: [
                            Expanded(
                              child: _buildLimitCard(
                                'Daily Limit',
                                Formatters.formatCurrency(
                                    _card!.dailyLimit),
                                _card!.spentToday,
                                _card!.dailyLimit,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildLimitCard(
                                'Monthly Limit',
                                Formatters.formatCurrency(
                                    _card!.monthlyLimit),
                                _card!.spentThisMonth,
                                _card!.monthlyLimit,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: ThemeConfig.cardColor,
                            borderRadius: BorderRadius.circular(
                                ThemeConfig.borderRadius),
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
                              _buildToggleRow(
                                'Contactless Payments',
                                _card!.isContactless,
                                (v) {},
                              ),
                              const Divider(),
                              _buildToggleRow(
                                'Online Transactions',
                                true,
                                (v) {},
                              ),
                              const Divider(),
                              _buildToggleRow(
                                'International Usage',
                                false,
                                (v) {},
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 24),
                        AppButton(
                          text: _card!.isActive
                              ? 'Block Card'
                              : 'Unblock Card',
                          onPressed: _toggleCardStatus,
                          isOutlined: true,
                          color: _card!.isActive
                              ? ThemeConfig.errorColor
                              : ThemeConfig.successColor,
                        ),
                        const SizedBox(height: 32),
                      ],
                    ),
                  ),
      ),
    );
  }

  Widget _buildNoCardView() {
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
              Icons.credit_card_outlined,
              size: 48,
              color: ThemeConfig.primaryColor,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'No Card Selected',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Select a card from the cards screen',
            style: TextStyle(color: ThemeConfig.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildCardInfo() {
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
          _buildInfoRow('Card Network', _card!.network.toUpperCase()),
          const Divider(),
          _buildInfoRow('Card Type',
              '${_card!.cardType.toUpperCase()} ${_card!.isVirtual ? '(Virtual)' : ''}'),
          const Divider(),
          _buildInfoRow('Status',
              Formatters.formatStatus(_card!.status)),
          const Divider(),
          _buildInfoRow(
            'Created',
            Formatters.formatDate(_card!.createdAt),
          ),
          if (_card!.activatedAt != null) ...[
            const Divider(),
            _buildInfoRow(
              'Activated',
              Formatters.formatDate(_card!.activatedAt!),
            ),
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
          Text(value,
              style: const TextStyle(
                  fontWeight: FontWeight.w500, fontSize: 14)),
        ],
      ),
    );
  }

  Widget _buildLimitCard(
      String title, String limit, double spent, double max) {
    final percentage = max > 0 ? spent / max : 0.0;
    return Container(
      padding: const EdgeInsets.all(16),
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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: const TextStyle(
                  fontSize: 12, color: ThemeConfig.textSecondary)),
          const SizedBox(height: 4),
          Text(limit,
              style: const TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(3),
            child: LinearProgressIndicator(
              value: percentage,
              backgroundColor: Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(
                percentage > 0.8
                    ? ThemeConfig.errorColor
                    : ThemeConfig.primaryColor,
              ),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '${(percentage * 100).toStringAsFixed(0)}% used',
            style: const TextStyle(
                fontSize: 11, color: ThemeConfig.textSecondary),
          ),
        ],
      ),
    );
  }

  Widget _buildToggleRow(
      String title, bool value, ValueChanged<bool> onChanged) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title,
            style: const TextStyle(fontSize: 14)),
        Switch(
          value: value,
          onChanged: onChanged,
          activeColor: ThemeConfig.primaryColor,
        ),
      ],
    );
  }

  void _showChangePinDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Change PIN'),
        content: const Text(
          'A new PIN will be sent to your registered mobile number.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('PIN change request submitted'),
                ),
              );
            },
            child: const Text('Request'),
          ),
        ],
      ),
    );
  }
}
