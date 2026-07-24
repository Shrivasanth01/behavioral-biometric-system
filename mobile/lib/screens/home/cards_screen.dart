import 'package:flutter/material.dart';
import '../../config/theme_config.dart';
import '../../models/card_model.dart';
import '../../services/banking_service.dart';
import '../../widgets/card_widget.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/empty_state.dart';
import '../../utils/behavioral_capture.dart';

class CardsScreen extends StatefulWidget {
  const CardsScreen({super.key});

  @override
  State<CardsScreen> createState() => _CardsScreenState();
}

class _CardsScreenState extends State<CardsScreen> {
  final BankingService _bankingService = BankingService();
  List<CardModel> _cards = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadCards();
  }

  Future<void> _loadCards() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      _cards = await _bankingService.getCards();
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
          title: const Text('My Cards'),
          actions: [
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: () => _showAddCardDialog(),
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: _loadCards,
          child: _isLoading && _cards.isEmpty
              ? const LoadingIndicator(message: 'Loading cards...')
              : _cards.isEmpty
                  ? const EmptyState(
                      icon: Icons.credit_card_outlined,
                      title: 'No cards yet',
                      subtitle:
                          'Add a debit or credit card to get started',
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _cards.length,
                      itemBuilder: (context, index) {
                        final card = _cards[index];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 20),
                          child: GestureDetector(
                            onTap: () {
                              Navigator.pushNamed(
                                context,
                                '/card-detail',
                                arguments: card.id,
                              );
                            },
                            child: CardWidget(card: card),
                          ),
                        );
                      },
                    ),
        ),
      ),
    );
  }

  void _showAddCardRequest() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
                margin: const EdgeInsets.only(bottom: 20),
                alignment: Alignment.center,
              ),
              const Text(
                'Request New Card',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),
              _buildCardTypeOption(
                icon: Icons.credit_card,
                title: 'Debit Card',
                subtitle: 'Linked to your savings account',
                onTap: () {
                  Navigator.pop(context);
                  _showAddCardDialog();
                },
              ),
              const SizedBox(height: 12),
              _buildCardTypeOption(
                icon: Icons.credit_card_outlined,
                title: 'Credit Card',
                subtitle: 'With rewards and benefits',
                onTap: () {
                  Navigator.pop(context);
                },
              ),
              const SizedBox(height: 12),
              _buildCardTypeOption(
                icon: Icons.phone_android,
                title: 'Virtual Card',
                subtitle: 'For online transactions',
                onTap: () {
                  Navigator.pop(context);
                  _showAddCardDialog();
                },
              ),
              const SizedBox(height: 24),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCardTypeOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: ThemeConfig.cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: ThemeConfig.dividerColor),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: ThemeConfig.primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: ThemeConfig.primaryColor),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: const TextStyle(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: const TextStyle(
                          fontSize: 12, color: ThemeConfig.textSecondary)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: ThemeConfig.textSecondary),
          ],
        ),
      ),
    );
  }

  void _showAddCardDialog() {
    final formKey = GlobalKey<FormState>();
    final networkController = TextEditingController();
    String selectedAccountId = '';

    showDialog(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          title: const Text('Request New Card'),
          content: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(
                    labelText: 'Card Type',
                    prefixIcon: Icon(Icons.credit_card),
                  ),
                  items: ['debit', 'credit', 'virtual']
                      .map((t) => DropdownMenuItem(
                          value: t,
                          child: Text(t[0].toUpperCase() + t.substring(1))))
                      .toList(),
                  onChanged: (v) {},
                ),
              ],
            ),
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
                    content: Text('Card request submitted!'),
                    backgroundColor: ThemeConfig.successColor,
                  ),
                );
              },
              child: const Text('Submit'),
            ),
          ],
        );
      },
    );
  }
}
