import 'package:flutter/material.dart';
import '../config/theme_config.dart';
import '../models/card_model.dart';
import '../utils/formatters.dart';

class CardWidget extends StatelessWidget {
  final CardModel card;
  final bool showFullDetails;
  final double height;

  const CardWidget({
    super.key,
    required this.card,
    this.showFullDetails = true,
    this.height = 200,
  });

  @override
  Widget build(BuildContext context) {
    final color = card.cardColor;
    return Container(
      height: height,
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(ThemeConfig.borderRadius),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            color,
            Color.lerp(color, Colors.black, 0.3)!,
            Color.lerp(color, Colors.black, 0.5)!,
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.4),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    card.cardHolderName.toUpperCase(),
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      letterSpacing: 1,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    card.cardType.toUpperCase(),
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.6),
                      fontSize: 10,
                      letterSpacing: 1,
                    ),
                  ),
                ],
              ),
              Image.asset(
                _getNetworkLogo(),
                height: 32,
                errorBuilder: (_, __, ___) => Text(
                  card.network.toUpperCase(),
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
              ),
            ],
          ),
          if (showFullDetails) ...[
            Text(
              card.maskedCardNumber,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
                letterSpacing: 3,
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'VALID THRU',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.5),
                        fontSize: 8,
                        letterSpacing: 1,
                      ),
                    ),
                    Text(
                      card.formattedExpiry,
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                Row(
                  children: [
                    if (card.isContactless)
                      Container(
                        margin: const EdgeInsets.only(right: 8),
                        child: Icon(
                          Icons.wifi,
                          color: Colors.white.withOpacity(0.8),
                          size: 20,
                        ),
                      ),
                    if (card.isVirtual)
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          'VIRTUAL',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.9),
                            fontSize: 8,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  String _getNetworkLogo() {
    switch (card.network) {
      case 'visa':
        return 'assets/logos/visa.png';
      case 'mastercard':
        return 'assets/logos/mastercard.png';
      case 'amex':
        return 'assets/logos/amex.png';
      default:
        return '';
    }
  }
}
