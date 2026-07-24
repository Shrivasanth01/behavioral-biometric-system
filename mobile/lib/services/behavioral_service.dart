import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../config/api_config.dart';
import '../models/behavioral_model.dart';
import 'api_service.dart';

class BehavioralService {
  final ApiService _api = ApiService();
  final List<BehavioralEvent> _eventBuffer = [];
  Timer? _uploadTimer;
  bool _isCollecting = false;

  void startCollection() {
    if (_isCollecting) return;
    _isCollecting = true;
    _uploadTimer = Timer.periodic(
      ApiConfig.behavioralUploadInterval,
      (_) => _flushEvents(),
    );
  }

  void stopCollection() {
    _isCollecting = false;
    _uploadTimer?.cancel();
    _uploadTimer = null;
    _flushEvents();
  }

  void captureEvent(String eventType, Map<String, dynamic> data) {
    if (!_isCollecting) return;
    _eventBuffer.add(BehavioralEvent(
      eventType: eventType,
      data: data,
    ));

    if (_eventBuffer.length >= 50) {
      _flushEvents();
    }
  }

  void captureTouchEvent({
    required double x,
    required double y,
    double pressure = 0.0,
    double area = 0.0,
    double duration = 0.0,
    String gestureType = 'tap',
  }) {
    captureEvent('touch', {
      'x': x,
      'y': y,
      'pressure': pressure,
      'area': area,
      'duration': duration,
      'gesture_type': gestureType,
    });
  }

  void captureSensorEvent(Map<String, dynamic> sensorData) {
    captureEvent('sensor', sensorData);
  }

  void captureNavigationEvent(String screen) {
    captureEvent('navigation', {
      'screen': screen,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  void captureGestureEvent(String gesture, Map<String, dynamic> details) {
    captureEvent('gesture', {
      'gesture': gesture,
      ...details,
    });
  }

  Future<void> _flushEvents() async {
    if (_eventBuffer.isEmpty) return;

    final events = List<BehavioralEvent>.from(_eventBuffer);
    _eventBuffer.clear();

    try {
      await _uploadEvents(events);
    } catch (e) {
      _eventBuffer.insertAll(0, events);
      if (_eventBuffer.length > 200) {
        _eventBuffer.removeRange(0, _eventBuffer.length - 200);
      }
    }
  }

  Future<void> _uploadEvents(List<BehavioralEvent> events) async {
    if (events.isEmpty) return;

    try {
      await _api.post(ApiConfig.behavioralEvents, body: {
        'events': events.map((e) => e.toJson()).toList(),
        'device_info': _getDeviceInfo(),
      });
    } catch (_) {}
  }

  Map<String, dynamic> _getDeviceInfo() {
    return {
      'platform': defaultTargetPlatform.toString(),
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  Future<BehavioralProfile> getBehavioralProfile() async {
    final response = await _api.get(ApiConfig.behavioralProfile);
    return BehavioralProfile.fromJson(response ?? {});
  }

  Future<double> getTrustScore() async {
    final response = await _api.get(ApiConfig.behavioralScore);
    return (response?['trust_score'] ?? response?['trustScore'] ?? 0.0).toDouble();
  }

  Future<Map<String, dynamic>> verifyBehavioral() async {
    final response = await _api.post(ApiConfig.behavioralVerify);
    return response ?? {};
  }

  Future<List<BehavioralEvent>> getPendingEvents() async {
    return List.unmodifiable(_eventBuffer);
  }

  bool get isCollecting => _isCollecting;
  int get bufferSize => _eventBuffer.length;

  void dispose() {
    stopCollection();
    _eventBuffer.clear();
  }
}
