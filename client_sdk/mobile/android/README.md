# Android SDK - Behavioral Biometrics Tracker

Kotlin-based behavioral biometric tracking SDK for Android applications.

## Features

- **Touch Events**: ACTION_DOWN, ACTION_MOVE, ACTION_UP with pressure, size, coordinates, orientation, tool type
- **Gesture Detection**: Swipe direction/velocity/acceleration, fling, pinch zoom, rotation, scroll
- **Keyboard Events**: Key press/release timing, repeat count, meta state, long press detection
- **Motion Sensors**: Accelerometer and gyroscope capture (when available)
- **Orientation Changes**: Portrait/landscape detection
- **App Lifecycle**: Activity create/start/resume/pause/stop/destroy tracking
- **Device Fingerprinting**: Android ID, build properties, screen metrics, RAM, CPU info, combined SHA-256 hash
- **Session Management**: Auto-generated UUID sessions, configurable timeout, activity-based extension
- **Batched Submission**: Periodic flush, exponential backoff retry, configurable batch size/interval

## Installation

Add to your app's `build.gradle.kts`:

```kotlin
dependencies {
    implementation("com.behavioral.biometric:sdk:1.0.0")
}
```

Or copy `BehaviorTracker.kt` directly into your project.

## Quick Start

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var tracker: BehaviorTracker

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tracker = BehaviorTracker.getInstance(this, BehaviorTracker.Config(
            userId = "user_123",
            endpoint = "https://api.example.com/events",
            enableLogging = true,
        ))
    }

    override fun onResume() {
        super.onResume()
        tracker.startCapture(this)
    }

    override fun onPause() {
        super.onPause()
        tracker.stopCapture()
    }
}
```

## Configuration

| Property | Default | Description |
|----------|---------|-------------|
| `userId` | `null` | User identifier |
| `endpoint` | `/api/events` | Server endpoint |
| `batchIntervalMs` | `5000` | Batch flush interval |
| `batchSize` | `50` | Max events before forced flush |
| `captureTouch` | `true` | Enable touch events |
| `captureMotion` | `true` | Enable motion tracking |
| `captureKeys` | `true` | Enable keyboard events |
| `captureSensors` | `true` | Enable accelerometer/gyroscope |
| `captureOrientation` | `true` | Enable orientation tracking |
| `captureLifecycle` | `true` | Enable lifecycle tracking |
| `sessionTimeoutMs` | `1800000` | Session inactivity timeout |
| `maxRetries` | `3` | Max retries on failure |
| `retryBaseDelayMs` | `1000` | Base retry delay |
| `enableLogging` | `false` | Enable logcat logging |
| `gestureVelocityUnits` | `1000` | Velocity tracker units |
| `sensorSamplingPeriodUs` | `SENSOR_DELAY_GAME` | Sensor sampling period |

## API Reference

### `getInstance(context, config)`
Returns the singleton instance.

### `startCapture(activity)`
Registers all listeners and begins tracking.

### `stopCapture()`
Flushes events, unregisters all listeners, stops tracking.

### `getTouchEventListener()`
Returns an `OnTouchListener` to attach to any View.

### `handleTouchEvent(event)`
Manually process a `MotionEvent`.

### `handleKeyEvent(event)`
Manually process a `KeyEvent`. Returns false to allow event propagation.

### `onConfigurationChanged(newConfig)`
Call from `Activity.onConfigurationChanged()`.

### `getDeviceFingerprint()`
Returns a JSONObject with device fingerprint components and combined hash.

### `getSessionData()`
Returns the current `SessionData` object.

### `submitEvents([endpoint])`
POSTs all buffered events to the server. Returns the response JSON.

### `getEvents()`
Returns a copy of buffered events.

### `getSessionId()`
Returns the current session ID.

### `getEventCount()`
Returns the number of buffered events.

### `clearEvents()`
Clears all buffered events.

### `resetInstance()`
Stops capture and clears the singleton.

## Event Categories

| Category | Events |
|----------|--------|
| `touch` | touch_down, touch_move, touch_up, touch_cancel |
| `gesture` | swipe, fling, pinch, zoom, rotation |
| `keyboard` | key_down, key_up |
| `sensor` | accelerometer, gyroscope, sensor_accuracy |
| `orientation` | orientation_change |
| `lifecycle` | activity_created, started, resumed, paused, stopped, destroyed |
| `system` | capture_started, capture_stopped |

## Fingerprint Components

- `deviceId` (Android ID, hashed)
- Build: `model`, `manufacturer`, `brand`, `product`, `device`, `hardware`, `board`
- System: `sdkInt`, `release`, `codename`, `buildType`, `buildTags`, `buildId`, `buildTime`
- Screen: `screenWidth`, `screenHeight`, `density`, `densityDpi`, `xdpi`, `ydpi`, `refreshRate`
- Device: `timezone`, `locale`, `totalRam`, `cpuInfo`
- `combinedHash` — SHA-256 of all fields
