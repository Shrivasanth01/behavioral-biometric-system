import 'dart:math';
import 'package:flutter/material.dart';
import '../config/theme_config.dart';

class BehavioralIndicator extends StatelessWidget {
  final double trustScore;
  final bool showDetails;
  final double size;

  const BehavioralIndicator({
    super.key,
    required this.trustScore,
    this.showDetails = true,
    this.size = 80,
  });

  @override
  Widget build(BuildContext context) {
    final level = _getTrustLevel();
    final color = _getTrustColor();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: CustomPaint(
            painter: _GaugePainter(
              trustScore: trustScore,
              color: color,
            ),
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '${trustScore.toStringAsFixed(0)}',
                    style: TextStyle(
                      fontSize: size * 0.3,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  Text(
                    '%',
                    style: TextStyle(
                      fontSize: size * 0.15,
                      fontWeight: FontWeight.w600,
                      color: color.withOpacity(0.7),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        if (showDetails) ...[
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 4,
            ),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              level.toUpperCase(),
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
              ),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Behavioral Trust Score',
            style: TextStyle(
              color: ThemeConfig.textSecondary,
              fontSize: 11,
            ),
          ),
        ],
      ],
    );
  }

  String _getTrustLevel() {
    if (trustScore >= 80) return 'high';
    if (trustScore >= 50) return 'medium';
    return 'low';
  }

  Color _getTrustColor() {
    if (trustScore >= 80) return ThemeConfig.trustHigh;
    if (trustScore >= 50) return ThemeConfig.trustMedium;
    return ThemeConfig.trustLow;
  }
}

class _GaugePainter extends CustomPainter {
  final double trustScore;
  final Color color;

  _GaugePainter({required this.trustScore, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;

    final bgPaint = Paint()
      ..color = Colors.grey.shade200
      ..style = PaintingStyle.stroke
      ..strokeWidth = 6
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, bgPaint);

    final progressPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 6
      ..strokeCap = StrokeCap.round;

    final sweepAngle = (trustScore / 100.0) * 2 * pi;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -pi / 2,
      sweepAngle,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _GaugePainter oldDelegate) {
    return oldDelegate.trustScore != trustScore;
  }
}

class BehavioralTrustBar extends StatelessWidget {
  final double trustScore;
  final bool showLabel;

  const BehavioralTrustBar({
    super.key,
    required this.trustScore,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = trustScore >= 80
        ? ThemeConfig.trustHigh
        : trustScore >= 50
            ? ThemeConfig.trustMedium
            : ThemeConfig.trustLow;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (showLabel)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Trust Score',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${trustScore.toStringAsFixed(0)}%',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ],
          ),
        if (showLabel) const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: trustScore / 100.0,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 8,
          ),
        ),
      ],
    );
  }
}
