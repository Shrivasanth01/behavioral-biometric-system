# Web SDK - Behavioral Biometrics Tracker

Browser-based behavioral biometric tracking SDK that captures user interaction patterns for identity verification.

## Features

- **Keyboard Tracking**: keydown/keyup with key, code, location, repeat, meta keys
- **Mouse Tracking**: mousemove (throttled), click, mousedown, mouseup, contextmenu, dblclick — with speed/acceleration
- **Touch Tracking**: touchstart, touchmove, touchend with pressure, radius, rotation
- **Scroll Tracking**: scroll (throttled), wheel with delta metrics
- **Focus Tracking**: focus, blur, focusin, focusout on elements
- **Clipboard Tracking**: copy, cut, paste actions
- **Resize Tracking**: window resize with dimensions
- **Visibility Tracking**: page visibility changes (tab hidden/visible)
- **Navigation Tracking**: popstate and beforeunload events
- **Device Fingerprinting**: Canvas, WebGL, AudioContext, screen, timezone, fonts, combined SHA-256 hash
- **Session Management**: Auto-generated session IDs, configurable timeout, activity-based freeze/resume
- **Batched Submission**: Periodic flush with configurable interval/size, exponential backoff retry
- **sendBeacon fallback**: Reliable delivery on page unload

## Installation

```html
<script src="tracker.js"></script>
```

## Quick Start

```javascript
const tracker = new BehavioralTracker({
  userId: 'user_123',
  endpoint: '/api/events',
  enableLogging: true,
});

tracker.start();
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `userId` | `null` | User identifier |
| `sessionId` | `null` | Auto-generated if not provided |
| `endpoint` | `/api/events` | Server endpoint for event submission |
| `batchInterval` | `5000` | Milliseconds between batch flushes |
| `batchSize` | `50` | Max events before forced flush |
| `throttleMousemove` | `50` | Mouse move throttle in ms |
| `throttleScroll` | `100` | Scroll throttle in ms |
| `captureKeys` | `true` | Enable keyboard events |
| `captureMouse` | `true` | Enable mouse events |
| `captureScroll` | `true` | Enable scroll events |
| `captureFocus` | `true` | Enable focus events |
| `captureTouch` | `true` | Enable touch events |
| `captureClipboard` | `true` | Enable clipboard events |
| `captureResize` | `true` | Enable resize events |
| `captureVisibility` | `true` | Enable visibility events |
| `captureNavigation` | `true` | Enable navigation events |
| `fingerprint` | `true` | Enable device fingerprinting |
| `enableLogging` | `false` | Enable console logging |
| `sessionTimeout` | `1800000` | Session inactivity timeout (30 min) |
| `maxRetries` | `3` | Max retries on batch failure |
| `retryBaseDelay` | `1000` | Base delay for retry backoff (ms) |

## API Reference

### `start()`
Attaches all event listeners and begins capturing.

### `stop()`
Flushes pending events, detaches all listeners, and stops capture.

### `getPayload()`
Returns the current session payload object with all buffered events.

### `submit([endpoint])`
POSTs all buffered events to the server endpoint. Returns the response JSON. Throws if no events recorded.

### `getFingerprint()`
Returns a promise resolving to the device fingerprint object with all components.

### `getSessionId()`
Returns the current session ID string.

### `clearEvents()`
Clears all buffered events.

### `getEventCount()`
Returns the number of buffered events.

### `onEvent(callback)`
Registers a callback invoked on each new event capture.

### `offEvent(callback)`
Removes a previously registered event callback.

### `destroy()`
Stops tracking, clears callbacks, events, and fingerprint.

## Event Format

```json
{
  "type": "keydown",
  "key": "a",
  "code": "KeyA",
  "location": 0,
  "repeat": false,
  "alt": false,
  "ctrl": false,
  "shift": false,
  "meta": false,
  "session_id": "sess_abc123",
  "ts": 1700000000000,
  "ts_perf": 1234.56,
  "page_url": "https://example.com"
}
```

## Fingerprint Components

- `canvasFingerprint` — Canvas rendering hash
- `webglVendor`, `webglRenderer` — GPU info
- `audioFingerprint` — AudioContext frequency data
- `installedFonts` — Detected system fonts
- `screenWidth`, `screenHeight`, `colorDepth`, `pixelDepth`
- `timezone`, `language`, `languages`
- `userAgent`, `platform`
- `hardwareConcurrency`, `deviceMemory`
- `combinedHash` — SHA-256 of all components

## Payload Structure

```json
{
  "session_id": "sess_abc123",
  "user_id": "user_123",
  "device_type": "web",
  "events": [...],
  "fingerprint": {...},
  "event_count": 150,
  "duration": 45000
}
```
