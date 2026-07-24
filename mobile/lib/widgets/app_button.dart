import 'package:flutter/material.dart';
import '../config/theme_config.dart';

class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool isOutlined;
  final bool isText;
  final bool isSmall;
  final IconData? icon;
  final Color? color;
  final Color? textColor;
  final double? width;

  const AppButton({
    super.key,
    required this.text,
    this.onPressed,
    this.isLoading = false,
    this.isOutlined = false,
    this.isText = false,
    this.isSmall = false,
    this.icon,
    this.color,
    this.textColor,
    this.width,
  });

  @override
  Widget build(BuildContext context) {
    if (isText) {
      return TextButton(
        onPressed: onPressed,
        child: Text(
          text,
          style: TextStyle(
            color: textColor ?? ThemeConfig.primaryColor,
            fontWeight: FontWeight.w600,
            fontSize: isSmall ? 14 : 16,
          ),
        ),
      );
    }

    if (isOutlined) {
      return SizedBox(
        width: width ?? double.infinity,
        height: isSmall ? 40 : 50,
        child: OutlinedButton(
          onPressed: onPressed,
          style: OutlinedButton.styleFrom(
            foregroundColor: textColor ?? color ?? ThemeConfig.primaryColor,
            side: BorderSide(color: color ?? ThemeConfig.primaryColor),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(ThemeConfig.smallRadius),
            ),
          ),
          child: _buildContent(context),
        ),
      );
    }

    return SizedBox(
      width: width ?? double.infinity,
      height: isSmall ? 40 : 50,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: color ?? ThemeConfig.primaryColor,
          foregroundColor: textColor ?? Colors.white,
          disabledBackgroundColor: Colors.grey.shade300,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(ThemeConfig.smallRadius),
          ),
        ),
        child: _buildContent(context),
      ),
    );
  }

  Widget _buildContent(BuildContext context) {
    if (isLoading) {
      return const SizedBox(
        width: 24,
        height: 24,
        child: CircularProgressIndicator(
          strokeWidth: 2.5,
          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
        ),
      );
    }

    if (icon != null) {
      return Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 8),
          Text(text),
        ],
      );
    }

    return Text(
      text,
      style: TextStyle(
        fontWeight: FontWeight.w600,
        fontSize: isSmall ? 14 : 16,
      ),
    );
  }
}
