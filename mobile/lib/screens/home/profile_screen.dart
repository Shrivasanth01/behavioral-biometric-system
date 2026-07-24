import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/auth_provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/behavioral_provider.dart';
import '../../widgets/app_button.dart';
import '../../widgets/behavioral_indicator.dart';
import '../../utils/formatters.dart';
import '../../utils/behavioral_capture.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final themeProvider = context.watch<ThemeProvider>();
    final behavioralProvider = context.watch<BehavioralProvider>();
    final user = authProvider.user;

    return BehavioralCaptureWidget(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Profile'),
          actions: [
            IconButton(
              icon: Icon(
                themeProvider.isDark
                    ? Icons.light_mode
                    : Icons.dark_mode,
              ),
              onPressed: () => themeProvider.toggleTheme(),
            ),
          ],
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              const SizedBox(height: 16),
              CircleAvatar(
                radius: 48,
                backgroundColor: ThemeConfig.primaryColor.withOpacity(0.1),
                child: Text(
                  user != null
                      ? Formatters.getInitials(user.fullName)
                      : '?',
                  style: const TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: ThemeConfig.primaryColor,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                user?.fullName ?? 'User',
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                user?.email ?? '',
                style: const TextStyle(
                  fontSize: 14,
                  color: ThemeConfig.textSecondary,
                ),
              ),
              const SizedBox(height: 32),
              if (behavioralProvider.isCollecting)
                Container(
                  margin: const EdgeInsets.only(bottom: 24),
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
                  child: Row(
                    children: [
                      BehavioralIndicator(
                        trustScore: behavioralProvider.trustScore,
                        size: 70,
                      ),
                      const SizedBox(width: 20),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Behavioral Trust Score',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 15,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              behavioralProvider.isCollecting
                                  ? 'Monitoring active'
                                  : 'Monitoring paused',
                              style: const TextStyle(
                                color: ThemeConfig.textSecondary,
                                fontSize: 12,
                              ),
                            ),
                            const SizedBox(height: 8),
                            BehavioralTrustBar(
                              trustScore: behavioralProvider.trustScore,
                              showLabel: false,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              _buildMenuSection('Account', [
                _buildMenuItem(
                  Icons.person_outline,
                  'Personal Details',
                  onTap: () {},
                ),
                _buildMenuItem(
                  Icons.shield_outlined,
                  'Security Settings',
                  onTap: () {
                    Navigator.pushNamed(context, '/mfa-setup');
                  },
                ),
                _buildMenuItem(
                  Icons.fingerprint,
                  'Biometric Login',
                  trailing: Switch(
                    value: true,
                    onChanged: (v) {},
                    activeColor: ThemeConfig.primaryColor,
                  ),
                ),
              ]),
              const SizedBox(height: 12),
              _buildMenuSection('Preferences', [
                _buildMenuItem(
                  Icons.notifications_outlined,
                  'Notifications',
                  onTap: () {},
                ),
                _buildMenuItem(
                  themeProvider.isDark
                      ? Icons.light_mode
                      : Icons.dark_mode,
                  'Dark Mode',
                  trailing: Switch(
                    value: themeProvider.isDark,
                    onChanged: (v) => themeProvider.toggleTheme(),
                    activeColor: ThemeConfig.primaryColor,
                  ),
                ),
                _buildMenuItem(
                  Icons.language,
                  'Language',
                  trailing: const Text(
                    'English',
                    style: TextStyle(
                      color: ThemeConfig.textSecondary,
                    ),
                  ),
                  onTap: () {},
                ),
              ]),
              const SizedBox(height: 12),
              _buildMenuSection('Support', [
                _buildMenuItem(
                  Icons.help_outline,
                  'Help Center',
                  onTap: () {},
                ),
                _buildMenuItem(
                  Icons.info_outline,
                  'About',
                  trailing: const Text(
                    'v1.0.0',
                    style: TextStyle(
                      color: ThemeConfig.textSecondary,
                    ),
                  ),
                  onTap: () {},
                ),
              ]),
              const SizedBox(height: 24),
              AppButton(
                text: 'Sign Out',
                onPressed: () async {
                  final confirmed = await showDialog<bool>(
                    context: context,
                    builder: (ctx) => AlertDialog(
                      title: const Text('Sign Out'),
                      content: const Text(
                        'Are you sure you want to sign out?',
                      ),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(ctx, false),
                          child: const Text('Cancel'),
                        ),
                        ElevatedButton(
                          onPressed: () => Navigator.pop(ctx, true),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: ThemeConfig.errorColor,
                          ),
                          child: const Text('Sign Out'),
                        ),
                      ],
                    ),
                  );

                  if (confirmed == true && mounted) {
                    await authProvider.logout();
                    if (mounted) {
                      Navigator.pushReplacementNamed(context, '/login');
                    }
                  }
                },
                isOutlined: true,
                color: ThemeConfig.errorColor,
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMenuSection(String title, List<Widget> items) {
    return Container(
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
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Text(
              title,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: ThemeConfig.textSecondary,
              ),
            ),
          ),
          ...items,
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    IconData icon,
    String title, {
    VoidCallback? onTap,
    Widget? trailing,
  }) {
    return ListTile(
      leading: Icon(icon, color: ThemeConfig.primaryColor),
      title: Text(
        title,
        style: const TextStyle(fontSize: 15),
      ),
      trailing: trailing ?? const Icon(Icons.chevron_right),
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
    );
  }
}
