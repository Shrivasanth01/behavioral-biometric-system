import 'package:flutter/material.dart';
import '../config/theme_config.dart';
import 'app_button.dart';

class ErrorState extends StatelessWidget {
  final String message;
  final String? actionLabel;
  final VoidCallback? onRetry;
  final IconData icon;

  const ErrorState({
    super.key,
    this.message = 'Something went wrong',
    this.actionLabel,
    this.onRetry,
    this.icon = Icons.error_outline,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                color: ThemeConfig.errorColor.withOpacity(0.08),
                borderRadius: BorderRadius.circular(48),
              ),
              child: Icon(
                icon,
                size: 48,
                color: ThemeConfig.errorColor.withOpacity(0.6),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Oops!',
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: ThemeConfig.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: const TextStyle(
                fontSize: 14,
                color: ThemeConfig.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              if (actionLabel != null)
                AppButton(
                  text: actionLabel!,
                  onPressed: onRetry,
                  icon: Icons.refresh,
                  isSmall: true,
                )
              else
                AppButton(
                  text: 'Try Again',
                  onPressed: onRetry,
                  icon: Icons.refresh,
                  isSmall: true,
                ),
            ],
          ],
        ),
      ),
    );
  }
}

class ErrorBanner extends StatelessWidget {
  final String message;
  final VoidCallback? onDismiss;

  const ErrorBanner({
    super.key,
    required this.message,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: 16,
        vertical: 12,
      ),
      decoration: BoxDecoration(
        color: ThemeConfig.errorColor.withOpacity(0.1),
        border: const Border(
          bottom: BorderSide(
            color: ThemeConfig.errorColor,
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.warning_amber_rounded,
            color: ThemeConfig.errorColor,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: ThemeConfig.errorColor,
                fontSize: 13,
              ),
            ),
          ),
          if (onDismiss != null)
            GestureDetector(
              onTap: onDismiss,
              child: const Icon(
                Icons.close,
                color: ThemeConfig.errorColor,
                size: 18,
              ),
            ),
        ],
      ),
    );
  }
}
