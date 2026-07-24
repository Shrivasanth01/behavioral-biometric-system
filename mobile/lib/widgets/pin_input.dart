import 'package:flutter/material.dart';
import '../config/theme_config.dart';

class PinInput extends StatefulWidget {
  final int pinLength;
  final ValueChanged<String> onCompleted;
  final String? error;

  const PinInput({
    super.key,
    this.pinLength = 4,
    required this.onCompleted,
    this.error,
  });

  @override
  State<PinInput> createState() => _PinInputState();
}

class _PinInputState extends State<PinInput> {
  final List<TextEditingController> _controllers = [];
  final List<FocusNode> _focusNodes = [];
  String _pin = '';

  @override
  void initState() {
    super.initState();
    for (int i = 0; i < widget.pinLength; i++) {
      _controllers.add(TextEditingController());
      _focusNodes.add(FocusNode());
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    for (final node in _focusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  void _onChanged(String value, int index) {
    if (value.length > 1) {
      value = value.substring(value.length - 1);
      _controllers[index].text = value;
      _controllers[index].selection = TextSelection.collapsed(offset: 1);
    }

    if (value.isNotEmpty) {
      if (index < widget.pinLength - 1) {
        _focusNodes[index + 1].requestFocus();
      } else {
        _focusNodes[index].unfocus();
        _buildPin();
      }
    }

    setState(() {});
  }

  void _onBackspace(int index) {
    if (index > 0 && _controllers[index].text.isEmpty) {
      _controllers[index - 1].clear();
      _focusNodes[index - 1].requestFocus();
    }
    _buildPin();
  }

  void _buildPin() {
    _pin = _controllers.map((c) => c.text).join();
    if (_pin.length == widget.pinLength) {
      widget.onCompleted(_pin);
    }
  }

  void clear() {
    for (final controller in _controllers) {
      controller.clear();
    }
    _pin = '';
    _focusNodes[0].requestFocus();
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(widget.pinLength, (index) {
            return Container(
              width: 56,
              height: 68,
              margin: const EdgeInsets.symmetric(horizontal: 6),
              decoration: BoxDecoration(
                color: ThemeConfig.cardColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: widget.error != null
                      ? ThemeConfig.errorColor
                      : _controllers[index].text.isNotEmpty
                          ? ThemeConfig.primaryColor
                          : ThemeConfig.dividerColor,
                  width: _controllers[index].text.isNotEmpty ? 2 : 1,
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: TextField(
                controller: _controllers[index],
                focusNode: _focusNodes[index],
                keyboardType: TextInputType.number,
                textAlign: TextAlign.center,
                maxLength: 1,
                obscureText: true,
                style: const TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  color: ThemeConfig.textPrimary,
                ),
                decoration: const InputDecoration(
                  counterText: '',
                  border: InputBorder.none,
                  enabledBorder: InputBorder.none,
                  focusedBorder: InputBorder.none,
                  contentPadding: EdgeInsets.only(bottom: 8),
                ),
                onChanged: (value) => _onChanged(value, index),
                onTap: () {
                  if (_controllers[index].text.isEmpty) {
                    for (int i = 0; i < widget.pinLength; i++) {
                      if (_controllers[i].text.isEmpty) {
                        _focusNodes[i].requestFocus();
                        break;
                      }
                    }
                  }
                },
              ),
            );
          }),
        ),
        if (widget.error != null)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Text(
              widget.error!,
              style: const TextStyle(
                color: ThemeConfig.errorColor,
                fontSize: 13,
              ),
            ),
          ),
      ],
    );
  }
}

class PinKeyboard extends StatelessWidget {
  final ValueChanged<String> onKeyPressed;
  final VoidCallback onBackspace;
  final VoidCallback? onBiometric;

  const PinKeyboard({
    super.key,
    required this.onKeyPressed,
    required this.onBackspace,
    this.onBiometric,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildRow(context, ['1', '2', '3']),
        _buildRow(context, ['4', '5', '6']),
        _buildRow(context, ['7', '8', '9']),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (onBiometric != null)
              _buildKey(context, Icons.fingerprint, onBiometric!),
            _buildKey(context, '0', () => onKeyPressed('0')),
            _buildKey(context, Icons.backspace_outlined, onBackspace),
          ],
        ),
      ],
    );
  }

  Widget _buildRow(BuildContext context, List<String> keys) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: keys.map((key) => _buildKey(context, key, () => onKeyPressed(key))).toList(),
    );
  }

  Widget _buildKey(BuildContext context, dynamic key, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 72,
        height: 72,
        margin: const EdgeInsets.all(6),
        decoration: BoxDecoration(
          color: ThemeConfig.cardColor,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Center(
          child: key is IconData
              ? Icon(key, size: 28, color: ThemeConfig.textPrimary)
              : Text(
                  key,
                  style: const TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w500,
                    color: ThemeConfig.textPrimary,
                  ),
                ),
        ),
      ),
    );
  }
}
