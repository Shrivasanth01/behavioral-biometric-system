import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:sensors_plus/sensors_plus.dart';
import '../models/behavioral_model.dart';

class SensorService {
  final List<SensorData> _sensorBuffer = [];
  StreamSubscription<AccelerometerEvent>? _accelSubscription;
  StreamSubscription<GyroscopeEvent>? _gyroSubscription;
  bool _isCollecting = false;
  static const int _maxBufferSize = 100;

  void startCollection() {
    if (_isCollecting) return;
    _isCollecting = true;

    _accelSubscription = accelerometerEventStream(
      samplingPeriod: const Duration(milliseconds: 100),
    ).listen(_onAccelerometerEvent);

    _gyroSubscription = gyroscopeEventStream(
      samplingPeriod: const Duration(milliseconds: 100),
    ).listen(_onGyroscopeEvent);
  }

  void stopCollection() {
    _isCollecting = false;
    _accelSubscription?.cancel();
    _accelSubscription = null;
    _gyroSubscription?.cancel();
    _gyroSubscription = null;
  }

  void _onAccelerometerEvent(AccelerometerEvent event) {
    _addSensorData(SensorData(
      accelX: event.x,
      accelY: event.y,
      accelZ: event.z,
    ));
  }

  void _onGyroscopeEvent(GyroscopeEvent event) {
    _addSensorData(SensorData(
      gyroX: event.x,
      gyroY: event.y,
      gyroZ: event.z,
    ));
  }

  void _addSensorData(SensorData data) {
    _sensorBuffer.add(data);
    if (_sensorBuffer.length > _maxBufferSize) {
      _sensorBuffer.removeAt(0);
    }
  }

  List<SensorData> getRecentSensorData({int count = 10}) {
    if (_sensorBuffer.isEmpty) return [];
    final start = (_sensorBuffer.length - count).clamp(0, _sensorBuffer.length);
    return _sensorBuffer.sublist(start);
  }

  List<SensorData> flushSensorData() {
    final data = List<SensorData>.from(_sensorBuffer);
    _sensorBuffer.clear();
    return data;
  }

  Map<String, double> getAverageSensorData() {
    if (_sensorBuffer.isEmpty) {
      return {
        'avg_accel_x': 0.0,
        'avg_accel_y': 0.0,
        'avg_accel_z': 0.0,
        'avg_gyro_x': 0.0,
        'avg_gyro_y': 0.0,
        'avg_gyro_z': 0.0,
      };
    }

    double sumAccelX = 0, sumAccelY = 0, sumAccelZ = 0;
    double sumGyroX = 0, sumGyroY = 0, sumGyroZ = 0;
    int accelCount = 0, gyroCount = 0;

    for (final data in _sensorBuffer) {
      if (data.accelX != null) {
        sumAccelX += data.accelX!;
        sumAccelY += data.accelY!;
        sumAccelZ += data.accelZ!;
        accelCount++;
      }
      if (data.gyroX != null) {
        sumGyroX += data.gyroX!;
        sumGyroY += data.gyroY!;
        sumGyroZ += data.gyroZ!;
        gyroCount++;
      }
    }

    return {
      'avg_accel_x': accelCount > 0 ? sumAccelX / accelCount : 0.0,
      'avg_accel_y': accelCount > 0 ? sumAccelY / accelCount : 0.0,
      'avg_accel_z': accelCount > 0 ? sumAccelZ / accelCount : 0.0,
      'avg_gyro_x': gyroCount > 0 ? sumGyroX / gyroCount : 0.0,
      'avg_gyro_y': gyroCount > 0 ? sumGyroY / gyroCount : 0.0,
      'avg_gyro_z': gyroCount > 0 ? sumGyroZ / gyroCount : 0.0,
    };
  }

  bool get isCollecting => _isCollecting;
  int get bufferSize => _sensorBuffer.length;

  void dispose() {
    stopCollection();
    _sensorBuffer.clear();
  }
}
