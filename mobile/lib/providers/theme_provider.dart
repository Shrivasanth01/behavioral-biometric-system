import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/theme_config.dart';

class ThemeProvider extends ChangeNotifier {
  ThemeData _themeData = ThemeConfig.lightTheme;
  bool _isDark = false;

  ThemeData get themeData => _themeData;
  bool get isDark => _isDark;

  ThemeProvider() {
    _loadTheme();
  }

  Future<void> _loadTheme() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _isDark = prefs.getBool('is_dark_theme') ?? false;
      _themeData = _isDark ? ThemeConfig.darkTheme : ThemeConfig.lightTheme;
      notifyListeners();
    } catch (_) {}
  }

  Future<void> toggleTheme() async {
    _isDark = !_isDark;
    _themeData = _isDark ? ThemeConfig.darkTheme : ThemeConfig.lightTheme;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('is_dark_theme', _isDark);
    } catch (_) {}
  }

  Future<void> setTheme(bool isDark) async {
    _isDark = isDark;
    _themeData = _isDark ? ThemeConfig.darkTheme : ThemeConfig.lightTheme;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('is_dark_theme', _isDark);
    } catch (_) {}
  }
}
