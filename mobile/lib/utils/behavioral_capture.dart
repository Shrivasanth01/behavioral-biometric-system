import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/behavioral_provider.dart';

class BehavioralCaptureWidget extends StatefulWidget {
  final Widget child;

  const BehavioralCaptureWidget({super.key, required this.child});

  @override
  State<BehavioralCaptureWidget> createState() =>
      _BehavioralCaptureWidgetState();
}

class _BehavioralCaptureWidgetState extends State<BehavioralCaptureWidget> {
  @override
  Widget build(BuildContext context) {
    return Listener(
      onPointerDown: (event) {
        final provider = context.read<BehavioralProvider>();
        provider.handleTouchEvent(
          x: event.position.dx,
          y: event.position.dy,
          pressure: event.pressure,
          area: event.area,
          duration: 0.0,
          gestureType: 'down',
        );
      },
      onPointerMove: (event) {
        final provider = context.read<BehavioralProvider>();
        provider.handleTouchEvent(
          x: event.position.dx,
          y: event.position.dy,
          pressure: event.pressure,
          area: event.area,
          duration: event.delta.distance,
          gestureType: 'move',
        );
      },
      onPointerUp: (event) {
        final provider = context.read<BehavioralProvider>();
        provider.handleTouchEvent(
          x: event.position.dx,
          y: event.position.dy,
          pressure: event.pressure,
          area: event.area,
          duration: 0.0,
          gestureType: 'up',
        );
      },
      onPointerCancel: (event) {
        final provider = context.read<BehavioralProvider>();
        provider.handleTouchEvent(
          x: event.position.dx,
          y: event.position.dy,
          pressure: event.pressure,
          area: event.area,
          duration: 0.0,
          gestureType: 'cancel',
        );
      },
      child: widget.child,
    );
  }
}

class BehavioralAwareScreen extends StatefulWidget {
  final Widget child;
  final String screenName;

  const BehavioralAwareScreen({
    super.key,
    required this.child,
    required this.screenName,
  });

  @override
  State<BehavioralAwareScreen> createState() => _BehavioralAwareScreenState();
}

class _BehavioralAwareScreenState extends State<BehavioralAwareScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BehavioralProvider>().handleNavigation(widget.screenName);
    });
  }

  @override
  Widget build(BuildContext context) {
    return BehavioralCaptureWidget(child: widget.child);
  }
}
