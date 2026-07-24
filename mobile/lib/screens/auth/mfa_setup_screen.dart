import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/app_button.dart';
import '../../widgets/loading_overlay.dart';

class MfaSetupScreen extends StatefulWidget {
  const MfaSetupScreen({super.key});

  @override
  State<MfaSetupScreen> createState() => _MfaSetupScreenState();
}

class _MfaSetupScreenState extends State<MfaSetupScreen> {
  String _selectedMethod = 'app';
  final _codeController = TextEditingController();
  bool _showVerifyStep = false;

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _setupMfa() async {
    final authProvider = context.read<AuthProvider>();
    final success = await authProvider.setupMfa(_selectedMethod);

    if (!mounted) return;

    if (success) {
      setState(() => _showVerifyStep = true);
    }
  }

  Future<void> _verifyCode() async {
    final authProvider = context.read<AuthProvider>();
    final verified = await authProvider.verifyMfa(_codeController.text.trim());

    if (!mounted) return;

    if (verified) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('MFA enabled successfully'),
          backgroundColor: ThemeConfig.successColor,
        ),
      );
      Navigator.pop(context, true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Two-Factor Authentication'),
      ),
      body: LoadingOverlay(
        isLoading: authProvider.isLoading,
        message: 'Setting up MFA...',
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: _showVerifyStep
              ? _buildVerifyStep(authProvider)
              : _buildSetupStep(authProvider),
        ),
      ),
    );
  }

  Widget _buildSetupStep(AuthProvider authProvider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 16),
        Container(
          width: 88,
          height: 88,
          decoration: BoxDecoration(
            color: ThemeConfig.primaryColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(22),
          ),
          child: const Icon(
            Icons.security,
            size: 48,
            color: ThemeConfig.primaryColor,
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          'Enhance Your Security',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          'Add an extra layer of security to your account',
          style: TextStyle(
            fontSize: 14,
            color: ThemeConfig.textSecondary,
          ),
        ),
        const SizedBox(height: 32),
        const Text(
          'Choose authentication method',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        _buildMethodOption(
          icon: Icons.phone_android,
          title: 'Authenticator App',
          subtitle: 'Google Authenticator, Authy, etc.',
          value: 'app',
        ),
        const SizedBox(height: 12),
        _buildMethodOption(
          icon: Icons.sms,
          title: 'SMS Authentication',
          subtitle: 'Receive codes via text message',
          value: 'sms',
        ),
        const SizedBox(height: 12),
        _buildMethodOption(
          icon: Icons.email,
          title: 'Email Authentication',
          subtitle: 'Receive codes via email',
          value: 'email',
        ),
        if (authProvider.error != null) ...[
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: ThemeConfig.errorColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              authProvider.error!,
              style: const TextStyle(
                color: ThemeConfig.errorColor,
                fontSize: 13,
              ),
            ),
          ),
        ],
        const SizedBox(height: 32),
        AppButton(
          text: 'Enable 2FA',
          onPressed: _setupMfa,
          isLoading: authProvider.isLoading,
          icon: Icons.shield,
        ),
      ],
    );
  }

  Widget _buildMethodOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required String value,
  }) {
    final isSelected = _selectedMethod == value;
    return GestureDetector(
      onTap: () => setState(() => _selectedMethod = value),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected
              ? ThemeConfig.primaryColor.withOpacity(0.05)
              : ThemeConfig.cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected
                ? ThemeConfig.primaryColor
                : ThemeConfig.dividerColor,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: isSelected
                    ? ThemeConfig.primaryColor.withOpacity(0.1)
                    : Colors.grey.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: isSelected
                    ? ThemeConfig.primaryColor
                    : ThemeConfig.textSecondary,
                size: 26,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 15,
                      color: isSelected
                          ? ThemeConfig.primaryColor
                          : ThemeConfig.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 12,
                      color: ThemeConfig.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              isSelected
                  ? Icons.radio_button_checked
                  : Icons.radio_button_off,
              color: isSelected
                  ? ThemeConfig.primaryColor
                  : ThemeConfig.textHint,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVerifyStep(AuthProvider authProvider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 32),
        Container(
          width: 88,
          height: 88,
          decoration: BoxDecoration(
            color: ThemeConfig.successColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(22),
          ),
          child: const Icon(
            Icons.check_circle_outline,
            size: 48,
            color: ThemeConfig.successColor,
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          'Verify Setup',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        const Text(
          'Enter the verification code shown in your authenticator app',
          style: TextStyle(
            fontSize: 14,
            color: ThemeConfig.textSecondary,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 32),
        TextFormField(
          controller: _codeController,
          keyboardType: TextInputType.number,
          textAlign: TextAlign.center,
          maxLength: 6,
          style: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            letterSpacing: 8,
          ),
          decoration: const InputDecoration(
            hintText: '000000',
            counterText: '',
          ),
        ),
        const SizedBox(height: 32),
        AppButton(
          text: 'Verify & Enable',
          onPressed: _verifyCode,
          isLoading: authProvider.isLoading,
        ),
        const SizedBox(height: 16),
        AppButton(
          text: 'Back',
          onPressed: () => setState(() => _showVerifyStep = false),
          isOutlined: true,
        ),
      ],
    );
  }
}
