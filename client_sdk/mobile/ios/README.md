# iOS SDK - Behavioral Biometrics Tracker

Swift-based behavioral biometric tracking SDK for iOS applications.

## Features

- **Touch Events**: UITouch phase, tapCount, force (3D Touch), major/minor radius, altitude/azimuth angle
- **Gesture Detection**: UITapGesture, UISwipeGesture (4 directions), UIPanGesture, UIPinchGesture, UIRotationGesture, UILongPressGesture, UIScreenEdgePanGesture
- **Swipe/Fling Analysis**: Direction, distance, speed, velocity, acceleration
- **Pinch/Zoom Detection**: Scale factor, velocity, focus point
- **Motion Sensors**: Accelerometer and gyroscope via CMMotionManager
- **Orientation Changes**: UIDevice orientation tracking (portrait, landscape, face up/down)
- **App Lifecycle**: didBecomeActive, willResignActive, didEnterBackground, willEnterForeground, willTerminate
- **Keyboard Notifications**: Keyboard show/hide events
- **Device Fingerprinting**: identifierForVendor, device model, system version, screen metrics, sysctl hw.machine/hw.model, combined SHA-256 hash
- **Session Management**: Auto-generated UUID sessions, configurable timeout, activity-based extension
- **Batched Submission**: Periodic flush, exponential backoff retry, configurable batch size/interval

## Installation

### Swift Package Manager

```swift
dependencies: [
    .package(url: "https://github.com/your-org/behavior-tracker-ios.git", from: "1.0.0")
]
```

### Manual

Copy `BehaviorTracker.swift` directly into your Xcode project.

You must also add `import CommonCrypto` (or set `CLANG_ENABLE_MODULES = YES` and add `Security.framework`).

## Quick Start

```swift
import UIKit

class ViewController: UIViewController {
    let tracker = BehaviorTracker(config: BehaviorTracker.Config(
        userId: "user_123",
        endpoint: "https://api.example.com/events",
        enableLogging: true
    ))

    override func viewDidLoad() {
        super.viewDidLoad()
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        tracker.startCapture(on: view)
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        tracker.stopCapture()
    }
}
```

## Configuration

| Property | Default | Description |
|----------|---------|-------------|
| `userId` | `nil` | User identifier |
| `endpoint` | `/api/events` | Server endpoint |
| `batchIntervalMs` | `5.0` | Batch flush interval (seconds) |
| `batchSize` | `50` | Max events before forced flush |
| `captureTouch` | `true` | Enable touch events |
| `captureGestures` | `true` | Enable gesture recognizers |
| `captureKeys` | `true` | Enable keyboard notifications |
| `captureSensors` | `true` | Enable accelerometer/gyroscope |
| `captureOrientation` | `true` | Enable orientation tracking |
| `captureLifecycle` | `true` | Enable lifecycle tracking |
| `sessionTimeoutSec` | `1800` | Session inactivity timeout (30 min) |
| `maxRetries` | `3` | Max retries on failure |
| `retryBaseDelaySec` | `1.0` | Base retry delay (seconds) |
| `enableLogging` | `false` | Enable console logging |
| `throttleIntervalMs` | `0.05` | Touch event throttle interval |

## API Reference

### `startCapture(on: UIView)`
Attaches gesture recognizers, sensor listeners, and notification observers to the given view.

### `stopCapture()`
Flushes events, removes gesture recognizers, stops sensors, unregisters observers.

### `handleTouch(_:in:)`
Manually process a UITouch event. Call from `touchesBegan/Moved/Ended/Cancelled`.

### `handleTap(_:)`
Handle UITapGestureRecognizer (automatically wired on startCapture).

### `handleSwipe(_:)`
Handle UISwipeGestureRecognizer (automatically wired for all 4 directions).

### `handlePan(_:)`
Handle UIPanGestureRecognizer with velocity/translation tracking.

### `handlePinch(_:)`
Handle UIPinchGestureRecognizer with scale tracking.

### `handleRotation(_:)`
Handle UIRotationGestureRecognizer with rotation tracking.

### `handleLongPress(_:)`
Handle UILongPressGestureRecognizer.

### `handleScreenEdge(_:)`
Handle UIScreenEdgePanGestureRecognizer.

### `getDeviceFingerprint()`
Returns a dictionary with device fingerprint components and combined SHA-256 hash.

### `getSessionData()`
Returns the current session dictionary.

### `submitEvents()`
POSTs all buffered events to the configured endpoint. Throws on failure.

### `submitEvents(to: String)`
POSTs all buffered events to the specified endpoint. Throws on failure.

### `getSessionId()`
Returns the current session ID string.

### `getEventCount()`
Returns the number of buffered events.

### `getEvents()`
Returns a copy of buffered events.

### `clearEvents()`
Clears all buffered events.

## Event Categories

| Category | Events |
|----------|--------|
| `touch` | touch_began, touch_moved, touch_stationary, touch_ended, touch_cancelled — with force, radius, altitude, azimuth |
| `gesture` | tap, swipe, pan, pinch, zoom, rotation, long_press, screen_edge, fling |
| `sensor` | accelerometer, gyroscope |
| `orientation` | portrait, portrait_upside_down, landscape_left, landscape_right, face_up, face_down |
| `lifecycle` | did_become_active, will_resign_active, did_enter_background, will_enter_foreground, will_terminate |
| `keyboard` | keyboard_will_show, keyboard_will_hide |
| `system` | capture_started, capture_stopped |

## Fingerprint Components

- `identifierForVendor` — Vendor IDFV
- `machine` — sysctl hw.machine (e.g. iPhone14,3)
- `hwModel` — sysctl hw.model
- `model`, `localizedModel`, `systemName`, `systemVersion`
- `screenWidth`, `screenHeight`, `screenScale`, `screenNativeBounds`, `screenNativeScale`
- `physicalMemory`, `processorCount`, `thermalState`
- `localeIdentifier`, `preferredLanguages`, `regionCode`, `currencyCode`
- `timezone`, `timezoneSecondsFromGMT`
- `deviceName`
- `combinedHash` — SHA-256 of all fields
