class BehavioralEvent {
  final String eventType;
  final Map<String, dynamic> data;
  final DateTime timestamp;

  BehavioralEvent({
    required this.eventType,
    required this.data,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'event_type': eventType,
      'data': data,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  factory BehavioralEvent.fromJson(Map<String, dynamic> json) {
    return BehavioralEvent(
      eventType: json['event_type'] ?? json['eventType'] ?? '',
      data: json['data'] ?? {},
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
    );
  }
}

class BehavioralProfile {
  final String userId;
  final double trustScore;
  final double confidenceLevel;
  final String riskLevel;
  final int totalEvents;
  final int anomaliesDetected;
  final DateTime lastAnalyzed;
  final Map<String, double> behavioralMetrics;

  BehavioralProfile({
    required this.userId,
    this.trustScore = 0.0,
    this.confidenceLevel = 0.0,
    this.riskLevel = 'medium',
    this.totalEvents = 0,
    this.anomaliesDetected = 0,
    DateTime? lastAnalyzed,
    this.behavioralMetrics = const {},
  }) : lastAnalyzed = lastAnalyzed ?? DateTime.now();

  factory BehavioralProfile.fromJson(Map<String, dynamic> json) {
    return BehavioralProfile(
      userId: json['user_id']?.toString() ?? json['userId'] ?? '',
      trustScore:
          (json['trust_score'] ?? json['trustScore'] ?? 0.0).toDouble(),
      confidenceLevel:
          (json['confidence_level'] ?? json['confidenceLevel'] ?? 0.0).toDouble(),
      riskLevel: json['risk_level'] ?? json['riskLevel'] ?? 'medium',
      totalEvents: json['total_events'] ?? json['totalEvents'] ?? 0,
      anomaliesDetected:
          json['anomalies_detected'] ?? json['anomaliesDetected'] ?? 0,
      lastAnalyzed: json['last_analyzed'] != null
          ? DateTime.parse(json['last_analyzed'])
          : (json['lastAnalyzed'] != null
              ? DateTime.parse(json['lastAnalyzed'])
              : DateTime.now()),
      behavioralMetrics:
          (json['behavioral_metrics'] ?? json['behavioralMetrics'] ?? {})
              .map((k, v) => MapEntry(k, v.toDouble())),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'trust_score': trustScore,
      'confidence_level': confidenceLevel,
      'risk_level': riskLevel,
      'total_events': totalEvents,
      'anomalies_detected': anomaliesDetected,
      'last_analyzed': lastAnalyzed.toIso8601String(),
      'behavioral_metrics': behavioralMetrics,
    };
  }
}

class SensorData {
  final double? accelX;
  final double? accelY;
  final double? accelZ;
  final double? gyroX;
  final double? gyroY;
  final double? gyroZ;
  final double? pressure;
  final double? lightLevel;
  final DateTime timestamp;

  SensorData({
    this.accelX,
    this.accelY,
    this.accelZ,
    this.gyroX,
    this.gyroY,
    this.gyroZ,
    this.pressure,
    this.lightLevel,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'accel_x': accelX,
      'accel_y': accelY,
      'accel_z': accelZ,
      'gyro_x': gyroX,
      'gyro_y': gyroY,
      'gyro_z': gyroZ,
      'pressure': pressure,
      'light_level': lightLevel,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

class TouchEvent {
  final double x;
  final double y;
  final double pressure;
  final double area;
  final double duration;
  final String gestureType;
  final DateTime timestamp;

  TouchEvent({
    required this.x,
    required this.y,
    this.pressure = 0.0,
    this.area = 0.0,
    this.duration = 0.0,
    this.gestureType = 'tap',
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'x': x,
      'y': y,
      'pressure': pressure,
      'area': area,
      'duration': duration,
      'gesture_type': gestureType,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}
