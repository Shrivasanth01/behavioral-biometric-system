# Mobile SDK Reference

## Overview

The mobile SDK provides behavioral biometrics capture for Flutter-based mobile applications. It captures touch gestures, device sensor data (accelerometer, gyroscope), and navigation patterns, then uploads them to the backend for behavioral profiling and risk assessment.

## Architecture

```
Flutter App
    │
    ├── BehavioralProvider (ChangeNotifier)
    │   ├── BehavioralService (event buffering + API upload)
    │   └── SensorService (accelerometer + gyroscope streams)
    │
    ├── BehavioralCaptureWidget (gesture listener widget)
    ├── BehavioralAwareScreen (screen-aware navigation tracker)
    └── BehavioralModel (event/model/trust score data classes)
```

## Installation

### pubspec.yaml

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  flutter_secure_storage: ^9.0.0
  sensors_plus: ^3.0.3
  provider: ^6.1.1
```

Add to your `pubspec.yaml`, then run:

```bash
flutter pub get
```

### Android Configuration

In `android/app/build.gradle`, ensure minimum SDK is 21+:

```gradle
android {
    defaultConfig {
        minSdkVersion 21
        targetSdkVersion 34
    }
}
```

Add permissions to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.VIBRATE"/>
```

### iOS Configuration

In `ios/Runner/Info.plist`:

```xml
<key>NSFaceIDUsageDescription</key>
<string>This app uses Face ID for biometric authentication</string>
```

No additional permissions needed for sensor data.

## Core Classes

### BehavioralEvent

Represents a single captured behavioral event.

```dart
class BehavioralEvent {
  final String eventType;       // 'touch', 'sensor', 'navigation', 'gesture'
  final Map<String, dynamic> data;  // event-specific payload
  final DateTime timestamp;

  BehavioralEvent({
    required this.eventType,
    required this.data,
    DateTime? timestamp,
  });

  Map<String, dynamic> toJson();
  factory BehavioralEvent.fromJson(Map<String, dynamic> json);
}
```

### BehavioralProfile

Represents the user's behavioral profile fetched from the backend.

```dart
class BehavioralProfile {
  final String userId;
  final double trustScore;          // 0.0 - 100.0
  final double confidenceLevel;     // 0.0 - 100.0
  final String riskLevel;           // 'low', 'medium', 'high'
  final int totalEvents;
  final int anomaliesDetected;
  final DateTime lastAnalyzed;
  final Map<String, double> behavioralMetrics;

  factory BehavioralProfile.fromJson(Map<String, dynamic> json);
  Map<String, dynamic> toJson();
}
```

### SensorData

Captured accelerometer/gyroscope reading.

```dart
class SensorData {
  final double? accelX, accelY, accelZ;
  final double? gyroX, gyroY, gyroZ;
  final double? pressure;
  final double? lightLevel;
  final DateTime timestamp;

  Map<String, dynamic> toJson();
}
```

### TouchEvent

Captured touch/gesture data.

```dart
class TouchEvent {
  final double x, y;
  final double pressure;
  final double area;
  final double duration;
  final String gestureType;  // 'tap', 'down', 'move', 'up', 'cancel'
  final DateTime timestamp;

  Map<String, dynamic> toJson();
}
```

## BehavioralService

Core service for event collection, buffering, and API upload.

### Methods

```dart
class BehavioralService {
  void startCollection();
  // Starts event buffering with a periodic upload timer (every 5 seconds)

  void stopCollection();
  // Stops collection and flushes remaining events

  void captureEvent(String eventType, Map<String, dynamic> data);
  // Generic event capture; stores in buffer, auto-flushes at 50 events

  void captureTouchEvent({
    required double x, required double y,
    double pressure = 0.0, double area = 0.0,
    double duration = 0.0, String gestureType = 'tap',
  });
  // Capture touch interaction with position, pressure, area, duration

  void captureSensorEvent(Map<String, dynamic> sensorData);
  // Capture sensor reading (accel/gyro)

  void captureNavigationEvent(String screen);
  // Capture screen navigation event

  void captureGestureEvent(String gesture, Map<String, dynamic> details);
  // Capture custom gesture event

  Future<BehavioralProfile> getBehavioralProfile();
  // GET /api/events/profile/{user_id}

  Future<double> getTrustScore();
  // GET /api/behavioral/trust-score → returns current trust score

  Future<Map<String, dynamic>> verifyBehavioral();
  // POST /api/behavioral/verify → triggers on-demand behavioral verification
}
```

### Event Upload Batching

| Setting | Default | Description |
|---------|---------|-------------|
| Buffer flush interval | 5 seconds | Periodic upload via `Timer.periodic` |
| Buffer flush size | 50 events | Immediate upload when buffer reaches threshold |
| Max buffer size | 200 events | Oldest events dropped if upload fails repeatedly |
| Upload endpoint | `POST /api/events/batch` | Backend batch ingestion endpoint |

On upload failure, events are re-inserted at buffer head and retried on next cycle.

## SensorService

Captures accelerometer and gyroscope data using `sensors_plus`.

### Methods

```dart
class SensorService {
  void startCollection();
  // Subscribes to accelerometer (100ms sampling period)
  // Subscribes to gyroscope (100ms sampling period)

  void stopCollection();
  // Cancels both subscriptions and clears buffer

  List<SensorData> getRecentSensorData({int count = 10});
  // Returns last N sensor readings without clearing

  List<SensorData> flushSensorData();
  // Returns all buffered readings and clears the buffer

  Map<String, double> getAverageSensorData();
  // Returns averaged sensor values:
  // { avg_accel_x, avg_accel_y, avg_accel_z,
  //   avg_gyro_x, avg_gyro_y, avg_gyro_z }
}
```

Buffer size: max 100 sensor readings (FIFO eviction).

## BehavioralProvider

State management provider (ChangeNotifier) that integrates both services.

### Properties

```dart
class BehavioralProvider extends ChangeNotifier {
  BehavioralProfile? get profile;        // Current behavioral profile
  double get trustScore;                 // 0.0 - 100.0
  bool get isCollecting;                 // Collection state
  bool get isLoading;                    // Profile loading state
  String? get error;                     // Last error message
  Map<String, double> get currentSensorAverages;  // Live sensor averages

  String get trustLevel;                 // 'high' (≥80), 'medium' (≥50), 'low'
}
```

### Methods

```dart
void startCollection();
// Initialize both BehavioralService and SensorService collection.
// Starts a periodic trust score update timer (every 30 seconds).

void stopCollection();
// Stop all collection and cancel timers.

void handleTouchEvent({x, y, pressure, area, duration, gestureType});
// Called from gesture listeners to capture touch events.

void handleSensorData();
// Fetches recent sensor data and captures via BehavioralService.

void handleNavigation(String screen);
// Called on screen transitions to capture navigation events.

Future<void> loadProfile();
// Fetch behavioral profile from backend.

Future<void> refreshTrustScore();
// Refresh trust score from backend.

void updateSensorAverages();
// Recalculate sensor averages from buffer.
```

### Trust Level Mapping

| Trust Score | Level | UI Indication |
|-------------|-------|---------------|
| 80 - 100 | `high` | Green indicator |
| 50 - 79 | `medium` | Yellow/amber indicator |
| 0 - 49 | `low` | Red indicator |

## Widget Integration

### BehavioralCaptureWidget

Wraps any widget subtree to capture touch gestures automatically.

```dart
BehavioralCaptureWidget(
  child: YourScreenContent(),
)
```

Captures: `onPointerDown`, `onPointerMove`, `onPointerUp`, `onPointerCancel`.
Each event is forwarded to `BehavioralProvider.handleTouchEvent()` with position, pressure, touch area, and gesture type.

### BehavioralAwareScreen

Combines navigation awareness with gesture capture.

```dart
BehavioralAwareScreen(
  screenName: 'dashboard',
  child: YourScreenContent(),
)
```

Automatically:
1. Reports navigation event on `initState`
2. Wraps child in `BehavioralCaptureWidget`
3. Screen name is sent to backend as part of behavioral profile

### Usage Example

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/behavioral_provider.dart';
import 'utils/behavioral_capture.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<BehavioralProvider>();
      provider.startCollection();
      provider.loadProfile();
    });
  }

  @override
  void dispose() {
    context.read<BehavioralProvider>().stopCollection();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BehavioralAwareScreen(
      screenName: 'dashboard',
      child: Consumer<BehavioralProvider>(
        builder: (context, bp, _) {
          return Column(
            children: [
              TrustScoreIndicator(score: bp.trustScore, level: bp.trustLevel),
              if (bp.isLoading)
                const CircularProgressIndicator()
              else
                ProfileSummary(profile: bp.profile),
            ],
          );
        },
      ),
    );
  }
}
```

## Trust Score Indicator Widget

```dart
class TrustScoreIndicator extends StatelessWidget {
  final double score;
  final String level;

  const TrustScoreIndicator({
    super.key,
    required this.score,
    required this.level,
  });

  @override
  Widget build(BuildContext context) {
    final color = level == 'high' ? Colors.green
        : level == 'medium' ? Colors.amber
        : Colors.red;

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.security, color: color, size: 20),
          const SizedBox(width: 8),
          Text(
            'Trust Score: ${score.toStringAsFixed(1)}',
            style: TextStyle(color: color, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}
```

## App Initialization Pattern

```dart
// main.dart
void main() {
  WidgetsFlutterBinding.ensureInitialized();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => AccountsProvider()),
        ChangeNotifierProvider(create: (_) => TransactionsProvider()),
        ChangeNotifierProvider(create: (_) => BehavioralProvider()),
      ],
      child: const BehavioralBiometricBankingApp(),
    ),
  );
}
```

## API Configuration

```dart
// config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'https://api.biobank.com';
  static const String behavioralEvents = '/api/events/batch';
  static const String behavioralProfile = '/api/events/profile';
  static const String behavioralScore = '/api/behavioral/trust-score';
  static const String behavioralVerify = '/api/behavioral/verify';
  static const Duration behavioralUploadInterval = Duration(seconds: 5);
}
```

## Event Data Format

### Touch Event
```json
{
  "event_type": "touch",
  "data": {
    "x": 156.3,
    "y": 302.1,
    "pressure": 0.85,
    "area": 12.4,
    "duration": 0.0,
    "gesture_type": "down"
  },
  "timestamp": "2026-06-14T10:30:00.123Z"
}
```

### Sensor Event
```json
{
  "event_type": "sensor",
  "data": {
    "accel_x": 0.12,
    "accel_y": 9.81,
    "accel_z": 0.34,
    "gyro_x": 0.01,
    "gyro_y": 0.02,
    "gyro_z": 0.00,
    "timestamp": "2026-06-14T10:30:00.456Z"
  },
  "timestamp": "2026-06-14T10:30:00.456Z"
}
```

### Navigation Event
```json
{
  "event_type": "navigation",
  "data": {
    "screen": "dashboard",
    "timestamp": "2026-06-14T10:30:00.789Z"
  },
  "timestamp": "2026-06-14T10:30:00.789Z"
}
```

## Batch Upload Format

```json
{
  "events": [ /* ... array of event objects ... */ ],
  "device_info": {
    "platform": "Android",
    "timestamp": "2026-06-14T10:30:05.000Z"
  }
}
```

## Data Collection Considerations

### Privacy

- All sensor data is processed locally on device
- Only derived behavioral features are uploaded to the backend
- Raw accelerometer/gyroscope data is not persisted on the server
- Event data is associated with user session, not individual identity
- Users can opt out via app settings (disables collection)

### Performance

- Sensor sampling rate: 100ms (10 Hz)
- Sensor buffer: 100 readings (10 seconds of data)
- Upload interval: 5 seconds
- Max buffer before forced upload: 50 events
- Network: batched upload reduces request overhead
- Battery: sensor collection is lightweight; auto-stops when app backgrounds

### Battery Impact

| Component | Impact | Notes |
|-----------|--------|-------|
| Touch capture | Negligible | Flutter gesture system already active |
| Accelerometer (10 Hz) | Low | ~2-5 mAh per hour |
| Gyroscope (10 Hz) | Low | ~3-6 mAh per hour |
| Network upload | Minimal | ~2-5 KB per batch, every 5 seconds |
| **Total estimated** | **~10 mAh/h** | Less than 0.5% of typical 3000 mAh battery |
