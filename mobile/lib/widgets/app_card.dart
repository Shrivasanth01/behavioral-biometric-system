import 'package:flutter/material.dart';
import '../config/theme_config.dart';

class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final double? elevation;
  final Color? color;
  final VoidCallback? onTap;
  final BorderRadiusGeometry? borderRadius;
  final EdgeInsetsGeometry? margin;

  const AppCard({
    super.key,
    required this.child,
    this.padding,
    this.elevation,
    this.color,
    this.onTap,
    this.borderRadius,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    final card = Card(
      margin: margin ?? EdgeInsets.zero,
      elevation: elevation ?? 2,
      color: color ?? ThemeConfig.cardColor,
      shape: RoundedRectangleBorder(
        borderRadius: borderRadius ?? BorderRadius.circular(ThemeConfig.borderRadius),
      ),
      child: Padding(
        padding: padding ?? const EdgeInsets.all(ThemeConfig.paddingMedium),
        child: child,
      ),
    );

    if (onTap != null) {
      return InkWell(
        onTap: onTap,
        borderRadius: borderRadius ?? BorderRadius.circular(ThemeConfig.borderRadius),
        child: card,
      );
    }

    return card;
  }
}
