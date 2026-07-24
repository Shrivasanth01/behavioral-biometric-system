import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/theme_config.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/app_button.dart';


class OtpVerificationScreen extends StatefulWidget {
  final String email;
  final String purpose;

  const OtpVerificationScreen({
    super.key,
    required this.email,
    this.purpose = 'verification',
  });

  @override
  State<OtpVerificationScreen> createState() => _OtpVerificationScreenState();
}

class _OtpVerificationScreenState extends State<OtpVerificationScreen> {
  final _otpControllers = List.generate(6, (_) => TextEditingController());
  final _otpFocusNodes = List.generate(6, (_) => FocusNode());
  Timer? _resendTimer;
  int _resendSeconds = 30;
  bool _canResend = false;

  @override
  void initState() {
    super.initState();
    _startResendTimer();
  }

  @override
  void dispose() {
    for (final c in _otpControllers) {
      c.dispose();
    }
    for (final f in _otpFocusNodes) {
      f.dispose();
    }
    _resendTimer?.cancel();
    super.dispose();
  }

  void _startResendTimer() {
    _canResend = false;
    _resendSeconds = 30;
    _resendTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_resendSeconds <= 1) {
        timer.cancel();
        if (mounted) setState(() => _canResend = true);
      } else {
        if (mounted) setState(() => _resendSeconds--);
      }
    });
  }

  void _onOtpChanged(String value, int index) {
    if (value.length > 1) {
      value = value.substring(value.length - 1);
      _otpControllers[index].text = value;
    }

    if (value.isNotEmpty && index < 5) {
      _otpFocusNodes[index + 1].requestFocus();
    }

    final otp = _otpControllers.map((c) => c.text).join();
    if (otp.length == 6) {
      _verifyOtp(otp);
    }
  }

  Future<void> _verifyOtp(String otp) async {
    final authProvider = context.read<AuthProvider>();
    final success = await authProvider.verifyOtp(
      widget.email,
      otp,
      widget.purpose,
    );

    if (!mounted) return;

    if (success) {
      Navigator.pop(context, true);
    }
  }

  Future<void> _resendOtp() async {
    if (!_canResend) return;
    final authProvider = context.read<AuthProvider>();
    await authProvider.forgotPassword(widget.email);
    _startResendTimer();
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Verify OTP'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const SizedBox(height: 32),
            Container(
              width: 88,
              height: 88,
              decoration: BoxDecoration(
                color: ThemeConfig.primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(22),
              ),
              child: const Icon(
                Icons.smartphone_outlined,
                size: 48,
                color: ThemeConfig.primaryColor,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'OTP Verification',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Enter the 6-digit code sent to\n${widget.email}',
              style: const TextStyle(
                fontSize: 14,
                color: ThemeConfig.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 40),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(6, (index) {
                return Container(
                  width: 48,
                  height: 56,
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  decoration: BoxDecoration(
                    color: ThemeConfig.cardColor,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: _otpControllers[index].text.isNotEmpty
                          ? ThemeConfig.primaryColor
                          : ThemeConfig.dividerColor,
                      width: _otpControllers[index].text.isNotEmpty ? 2 : 1,
                    ),
                  ),
                  child: TextField(
                    controller: _otpControllers[index],
                    focusNode: _otpFocusNodes[index],
                    keyboardType: TextInputType.number,
                    textAlign: TextAlign.center,
                    maxLength: 1,
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                    decoration: const InputDecoration(
                      counterText: '',
                      border: InputBorder.none,
                      enabledBorder: InputBorder.none,
                      focusedBorder: InputBorder.none,
                      contentPadding: EdgeInsets.only(bottom: 8),
                    ),
                    onChanged: (v) => _onOtpChanged(v, index),
                  ),
                );
              }),
            ),
            if (authProvider.error != null) ...[
              const SizedBox(height: 20),
              Text(
                authProvider.error!,
                style: const TextStyle(
                  color: ThemeConfig.errorColor,
                  fontSize: 13,
                ),
              ),
            ],
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: AppButton(
                text: 'Verify OTP',
                onPressed: () {
                  final otp = _otpControllers.map((c) => c.text).join();
                  if (otp.length == 6) _verifyOtp(otp);
                },
                isLoading: authProvider.isLoading,
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  _canResend
                      ? "Didn't receive the code? "
                      : 'Resend in $_resendSeconds s',
                  style: const TextStyle(
                    color: ThemeConfig.textSecondary,
                    fontSize: 13,
                  ),
                ),
                if (_canResend)
                  TextButton(
                    onPressed: _resendOtp,
                    child: const Text(
                      'Resend',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: ThemeConfig.primaryColor,
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
