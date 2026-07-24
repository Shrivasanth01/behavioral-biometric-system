# Behavioral Biometric SDKs

Multi-platform client SDKs for capturing behavioral biometric signals — keystroke dynamics, mouse/touch gestures, device motion, and interaction patterns — for continuous authentication and fraud detection.

## Platforms

| SDK | Path | Language | Lines |
|-----|------|----------|-------|
| Web | [`client_sdk/web/tracker.js`](web/tracker.js) | JavaScript | 350+ |
| Android | [`client_sdk/mobile/android/BehaviorTracker.kt`](mobile/android/BehaviorTracker.kt) | Kotlin | 500+ |
| iOS | [`client_sdk/mobile/ios/BehaviorTracker.swift`](mobile/ios/BehaviorTracker.swift) | Swift | 500+ |

## Features

### Common Across All Platforms
- Keyboard/touch event capture with timing accuracy
- Gesture detection (swipe, fling, pinch, zoom, rotation)
- Device motion tracking (accelerometer, gyroscope)
- Orientation change detection
- App lifecycle tracking
- Device fingerprinting with SHA-256 combined hash
- Session management with configurable timeouts
- Batched event submission with exponential backoff retry
- Configurable capture categories

### Web-Specific
- Mouse tracking with speed and acceleration
- Scroll tracking (throttled)
- Focus/blur/focusin/focusout on DOM elements
- Clipboard events (copy, cut, paste)
- Window resize tracking
- Page visibility (tab focus)
- Navigation (popstate, beforeunload with sendBeacon)
- Canvas, WebGL, AudioContext fingerprinting
- Installed font detection
- Event throttling

### Android-Specific
- MotionEvent with pressure, size, orientation, tool type
- VelocityTracker for fling detection
- Multi-touch pinch zoom and rotation
- SensorManager for accelerometer/gyroscope
- Activity lifecycle callbacks
- Build property fingerprinting
- /proc/meminfo and /proc/cpuinfo reading
- Settings.Secure.ANDROID_ID

### iOS-Specific
- UITouch with force (3D Touch), radius, altitudeAngle, azimuthAngle
- UIGestureRecognizer subclasses for all gesture types
- CMMotionManager for accelerometer/gyroscope
- UIDevice orientation notifications
- UIApplication lifecycle notifications (willTerminate flushes synchronously)
- sysctl hw.machine / hw.model fingerprinting
- identifierForVendor (IDFV)
- URLSession with semaphore-based synchronous submission

## Data Flow

```
User Interaction → SDK Capture → Local Buffer → Batch Timer → HTTP POST → Server
                    (events)        (memory)     (interval)    (JSON)     (API)
```

Each event includes:
- `session_id` — auto-generated UUID per session
- `ts` — epoch timestamp in milliseconds
- `ts_uptime` — system uptime in milliseconds (for relative timing)
- `category` — event category (touch, gesture, keyboard, sensor, etc.)
- Platform-specific data fields

## Payload Structure

```json
{
  "session_id": "sess_a1b2c3d4",
  "user_id": "usr_123",
  "device_type": "web|android|ios",
  "events": [
    {
      "category": "touch",
      "session_id": "sess_a1b2c3d4",
      "ts": 1700000000000,
      "ts_uptime": 123456.789,
      "type": "touch_began",
      "x": 150.0,
      "y": 300.0,
      "pressure": 0.8
    }
  ],
  "fingerprint": {
    "combinedHash": "sha256hash...",
    "platform": "..."
  },
  "event_count": 250,
  "duration": 60000
}
```

## Usage Guides

- [Web SDK Documentation](web/README.md)
- [Android SDK Documentation](mobile/android/README.md)
- [iOS SDK Documentation](mobile/ios/README.md)

## License

Proprietary. All rights reserved.
