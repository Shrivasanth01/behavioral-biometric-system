import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/behavioral_model.dart';
import '../services/behavioral_service.dart';
import '../services/sensor_service.dart';

class BehavioralProvider extends ChangeNotifier {
  final BehavioralService _behavioralService = BehavioralService();
  final SensorService _sensorService = SensorService();

  BehavioralProfile? _profile;
  double _trustScore = 0.0;
  bool _isCollecting = false;
  bool _isLoading = false;
  String? _error;
  Timer? _scoreUpdateTimer;
  Map<String, double> _currentSensorAverages = {};

  BehavioralProfile? get profile => _profile;
  double get trustScore => _trustScore;
  bool get isCollecting => _isCollecting;
  bool get isLoading => _isLoading;
  String? get error => _error;
  Map<String, double> get currentSensorAverages => _currentSensorAverages;

  String get trustLevel {
    if (_trustScore >= 80) return 'high';
    if (_trustScore >= 50) return 'medium';
    return 'low';
  }

  void startCollection() {
    if (_isCollecting) return;
    _isCollecting = true;

    _behavioralService.startCollection();
    _sensorService.startCollection();

    _scoreUpdateTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _updateTrustScore(),
    );

    notifyListeners();
  }

  void stopCollection() {
    _isCollecting = false;
    _behavioralService.stopCollection();
    _sensorService.stopCollection();
    _scoreUpdateTimer?.cancel();
    _scoreUpdateTimer = null;
    notifyListeners();
  }

  Future<void> _updateTrustScore() async {
    try {
      _trustScore = await _behavioralService.getTrustScore();
      _currentSensorAverages = _sensorService.getAverageSensorData();
      notifyListeners();
    } catch (_) {}
  }

  void handleTouchEvent({
    required double x,
    required double y,
    double pressure = 0.0,
    double area = 0.0,
    double duration = 0.0,
    String gestureType = 'tap',
  }) {
    if (!_isCollecting) return;

    _behavioralService.captureTouchEvent(
      x: x,
      y: y,
      pressure: pressure,
      area: area,
      duration: duration,
      gestureType: gestureType,
    );
  }

  void handleSensorData() {
    if (!_isCollecting) return;
    final sensorData = _sensorService.getRecentSensorData(count: 5);
    for (final data in sensorData) {
      _behavioralService.captureSensorEvent(data.toJson());
    }
  }

  void handleNavigation(String screen) {
    if (!_isCollecting) return;
    _behavioralService.captureNavigationEvent(screen);
  }

  Future<void> loadProfile() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _profile = await _behavioralService.getBehavioralProfile();
      _trustScore = _profile?.trustScore ?? 0.0;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refreshTrustScore() async {
    try {
      _trustScore = await _behavioralService.getTrustScore();
      notifyListeners();
    } catch (_) {}
  }

  void updateSensorAverages() {
    _currentSensorAverages = _sensorService.getAverageSensorData();
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  @override
  void dispose() {
    stopCollection();
    _scoreUpdateTimer?.cancel();
    super.dispose();
  }
}
