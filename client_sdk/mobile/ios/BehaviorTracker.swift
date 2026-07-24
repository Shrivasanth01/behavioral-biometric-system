import Foundation
import UIKit
import CoreMotion

@objc public class BehaviorTracker: NSObject {
    @objc public class Config: NSObject {
        @objc public var userId: String?
        @objc public var endpoint: String = "/api/events"
        @objc public var batchIntervalMs: TimeInterval = 5.0
        @objc public var batchSize: Int = 50
        @objc public var captureTouch: Bool = true
        @objc public var captureGestures: Bool = true
        @objc public var captureKeys: Bool = true
        @objc public var captureSensors: Bool = true
        @objc public var captureOrientation: Bool = true
        @objc public var captureLifecycle: Bool = true
        @objc public var sessionTimeoutSec: TimeInterval = 1800
        @objc public var maxRetries: Int = 3
        @objc public var retryBaseDelaySec: TimeInterval = 1.0
        @objc public var enableLogging: Bool = false
        @objc public var throttleIntervalMs: TimeInterval = 0.05

        @objc public init(
            userId: String? = nil,
            endpoint: String = "/api/events",
            batchIntervalMs: TimeInterval = 5.0,
            batchSize: Int = 50,
            captureTouch: Bool = true,
            captureGestures: Bool = true,
            captureKeys: Bool = true,
            captureSensors: Bool = true,
            captureOrientation: Bool = true,
            captureLifecycle: Bool = true,
            sessionTimeoutSec: TimeInterval = 1800,
            maxRetries: Int = 3,
            retryBaseDelaySec: TimeInterval = 1.0,
            enableLogging: Bool = false,
            throttleIntervalMs: TimeInterval = 0.05
        ) {
            self.userId = userId
            self.endpoint = endpoint
            self.batchIntervalMs = batchIntervalMs
            self.batchSize = batchSize
            self.captureTouch = captureTouch
            self.captureGestures = captureGestures
            self.captureKeys = captureKeys
            self.captureSensors = captureSensors
            self.captureOrientation = captureOrientation
            self.captureLifecycle = captureLifecycle
            self.sessionTimeoutSec = sessionTimeoutSec
            self.maxRetries = maxRetries
            self.retryBaseDelaySec = retryBaseDelaySec
            self.enableLogging = enableLogging
            self.throttleIntervalMs = throttleIntervalMs
            super.init()
        }
    }

    @objc public class TouchEventData: NSObject {
        @objc let type: String
        @objc let phase: Int
        @objc let tapCount: Int
        @objc let force: CGFloat
        @objc let majorRadius: CGFloat
        @objc let minorRadius: CGFloat
        @objc let locationX: CGFloat
        @objc let locationY: CGFloat
        @objc let previousLocationX: CGFloat
        @objc let previousLocationY: CGFloat
        @objc let timestamp: TimeInterval
        @objc let estimationUpdateIndex: Int
        @objc let estimatedPropertiesExpectingUpdates: Int
        @objc let altitudeAngle: CGFloat
        @objc let azimuthAngle: CGFloat
        @objc let azimuthUnitVectorX: CGFloat
        @objc let azimuthUnitVectorY: CGFloat

        init(touch: UITouch, view: UIView?) {
            let loc = touch.location(in: view)
            let prevLoc = touch.previousLocation(in: view)
            type = {
                switch touch.phase {
                case .began: return "touch_began"
                case .moved: return "touch_moved"
                case .stationary: return "touch_stationary"
                case .ended: return "touch_ended"
                case .cancelled: return "touch_cancelled"
                @unknown default: return "touch_unknown"
                }
            }()
            phase = touch.phase.rawValue
            tapCount = touch.tapCount
            force = touch.force
            majorRadius = touch.majorRadius
            minorRadius = touch.majorRadiusMinor
            locationX = loc.x
            locationY = loc.y
            previousLocationX = prevLoc.x
            previousLocationY = prevLoc.y
            timestamp = touch.timestamp
            estimationUpdateIndex = touch.estimationUpdateIndex?.intValue ?? 0
            estimatedPropertiesExpectingUpdates = touch.estimatedPropertiesExpectingUpdates.rawValue
            altitudeAngle = touch.altitudeAngle
            azimuthAngle = touch.azimuthAngle(in: view)
            let azVec = touch.azimuthUnitVector(in: view)
            azimuthUnitVectorX = azVec.dx
            azimuthUnitVectorY = azVec.dy
            super.init()
        }
    }

    @objc public class GestureEventData: NSObject {
        @objc let type: String
        @objc let state: Int
        @objc let locationX: CGFloat
        @objc let locationY: CGFloat
        @objc let velocityX: CGFloat
        @objc let velocityY: CGFloat
        @objc let velocity: CGFloat
        @objc let translationX: CGFloat
        @objc let translationY: CGFloat
        @objc let scale: CGFloat
        @objc let rotation: CGFloat
        @objc let direction: String?
        @objc let numberOfTouches: Int
        @objc let durationMs: TimeInterval

        init(type: String, gesture: UIGestureRecognizer) {
            self.type = type
            state = gesture.state.rawValue
            let loc = gesture.location(in: gesture.view)
            locationX = loc.x
            locationY = loc.y
            numberOfTouches = gesture.numberOfTouches
            durationMs = 0
            velocityX = 0
            velocityY = 0
            velocity = 0
            translationX = 0
            translationY = 0
            scale = 1
            rotation = 0
            direction = nil
            super.init()
        }
    }

    @objc public class SwipeGestureData: GestureEventData {
        override init(type: String, gesture: UIGestureRecognizer) {
            super.init(type: type, gesture: gesture)
            if let swipe = gesture as? UISwipeGestureRecognizer {
                direction = ["", "right", "left", "up", "down"][swipe.direction.rawValue]
            }
        }
    }

    @objc public class PanGestureData: GestureEventData {
        override init(type: String, gesture: UIGestureRecognizer) {
            super.init(type: type, gesture: gesture)
            if let pan = gesture as? UIPanGestureRecognizer {
                let vel = pan.velocity(in: pan.view)
                let trans = pan.translation(in: pan.view)
                velocityX = vel.x
                velocityY = vel.y
                velocity = sqrt(vel.x * vel.x + vel.y * vel.y)
                translationX = trans.x
                translationY = trans.y
            }
        }
    }

    @objc public class PinchGestureData: GestureEventData {
        override init(type: String, gesture: UIGestureRecognizer) {
            super.init(type: type, gesture: gesture)
            if let pinch = gesture as? UIPinchGestureRecognizer {
                scale = pinch.scale
                velocity = pinch.velocity
            }
        }
    }

    @objc public class RotationGestureData: GestureEventData {
        override init(type: String, gesture: UIGestureRecognizer) {
            super.init(type: type, gesture: gesture)
            if let rot = gesture as? UIRotationGestureRecognizer {
                rotation = rot.rotation
                velocity = rot.velocity
            }
        }
    }

    @objc public class LongPressGestureData: GestureEventData {
        override init(type: String, gesture: UIGestureRecognizer) {
            super.init(type: type, gesture: gesture)
            if let lp = gesture as? UILongPressGestureRecognizer {
                durationMs = lp.minimumPressDuration * 1000
                numberOfTouches = lp.numberOfTouchesRequired
            }
        }
    }

    @objc public class MotionEventData: NSObject {
        @objc let type: String
        @objc let x: Double
        @objc let y: Double
        @objc let z: Double
        @objc let timestamp: TimeInterval

        init(type: String, x: Double, y: Double, z: Double, timestamp: TimeInterval) {
            self.type = type
            self.x = x
            self.y = y
            self.z = z
            self.timestamp = timestamp
            super.init()
        }
    }

    @objc public class KeyboardEventData: NSObject {
        @objc let type: String
        @objc let characters: String
        @objc let charactersIgnoringModifiers: String
        @objc let modifierFlags: Int
        @objc let keyCode: Int
        @objc let isRepeat: Bool

        init(notification: Notification, isKeyDown: Bool) {
            type = isKeyDown ? "keyboard_will_show" : "keyboard_will_hide"
            if let userInfo = notification.userInfo {
                characters = userInfo[UIResponder.keyboardFocusedItemInfoKey] as? String ?? ""
            } else {
                characters = ""
            }
            charactersIgnoringModifiers = ""
            modifierFlags = 0
            keyCode = 0
            isRepeat = false
            super.init()
        }
    }

    // MARK: - Properties

    private let config: Config
    private let motionManager = CMMotionManager()
    private var sessionId: String
    private var events: [[String: Any]] = []
    private var isTracking = false
    private var retryCount = 0
    private var lastActivityTs: TimeInterval = 0
    private var sessionStartTs: TimeInterval = 0
    private var batchTimer: Timer?
    private var sessionTimer: Timer?
    private var fingerprintCache: [String: Any]?
    private var lastTouchLocation: CGPoint?
    private var touchStartTime: TimeInterval = 0

    private let eventQueue = DispatchQueue(label: "com.behavioral.biometric.events")
    private let networkQueue = DispatchQueue(label: "com.behavioral.biometric.network", qos: .background)

    private var orientationObserver: NSObjectProtocol?
    private var lifecycleObserver: NSObjectProtocol?
    private var keyboardWillShowObserver: NSObjectProtocol?
    private var keyboardWillHideObserver: NSObjectProtocol?

    private weak var targetView: UIView?
    private var gestureRecognizers: [UIGestureRecognizer] = []

    // MARK: - Initialization

    @objc public init(config: Config = Config()) {
        self.config = config
        self.sessionId = UUID().uuidString
        super.init()
    }

    // MARK: - Public API

    @objc public func startCapture(on view: UIView) {
        guard !isTracking else { return }
        isTracking = true
        targetView = view
        sessionId = UUID().uuidString
        sessionStartTs = Date().timeIntervalSince1970
        lastActivityTs = sessionStartTs
        events.removeAll()

        log("Starting capture, session: \(sessionId)")

        if config.captureTouch {
            let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
            tapGesture.cancelsTouchesInView = false
            view.addGestureRecognizer(tapGesture)
            gestureRecognizers.append(tapGesture)

            let swipeRight = UISwipeGestureRecognizer(target: self, action: #selector(handleSwipe(_:)))
            swipeRight.direction = .right
            view.addGestureRecognizer(swipeRight)
            gestureRecognizers.append(swipeRight)

            let swipeLeft = UISwipeGestureRecognizer(target: self, action: #selector(handleSwipe(_:)))
            swipeLeft.direction = .left
            view.addGestureRecognizer(swipeLeft)
            gestureRecognizers.append(swipeLeft)

            let swipeUp = UISwipeGestureRecognizer(target: self, action: #selector(handleSwipe(_:)))
            swipeUp.direction = .up
            view.addGestureRecognizer(swipeUp)
            gestureRecognizers.append(swipeUp)

            let swipeDown = UISwipeGestureRecognizer(target: self, action: #selector(handleSwipe(_:)))
            swipeDown.direction = .down
            view.addGestureRecognizer(swipeDown)
            gestureRecognizers.append(swipeDown)

            let panGesture = UIPanGestureRecognizer(target: self, action: #selector(handlePan(_:)))
            panGesture.cancelsTouchesInView = false
            panGesture.maximumNumberOfTouches = 5
            view.addGestureRecognizer(panGesture)
            gestureRecognizers.append(panGesture)

            let pinchGesture = UIPinchGestureRecognizer(target: self, action: #selector(handlePinch(_:)))
            pinchGesture.cancelsTouchesInView = false
            view.addGestureRecognizer(pinchGesture)
            gestureRecognizers.append(pinchGesture)

            let rotationGesture = UIRotationGestureRecognizer(target: self, action: #selector(handleRotation(_:)))
            rotationGesture.cancelsTouchesInView = false
            view.addGestureRecognizer(rotationGesture)
            gestureRecognizers.append(rotationGesture)

            let longPressGesture = UILongPressGestureRecognizer(target: self, action: #selector(handleLongPress(_:)))
            longPressGesture.cancelsTouchesInView = false
            view.addGestureRecognizer(longPressGesture)
            gestureRecognizers.append(longPressGesture)

            let screenEdgeGesture = UIScreenEdgePanGestureRecognizer(target: self, action: #selector(handleScreenEdge(_:)))
            screenEdgeGesture.edges = .all
            view.addGestureRecognizer(screenEdgeGesture)
            gestureRecognizers.append(screenEdgeGesture)
        }

        if config.captureOrientation {
            orientationObserver = NotificationCenter.default.addObserver(
                forName: UIDevice.orientationDidChangeNotification,
                object: nil, queue: .main
            ) { [weak self] _ in
                self?.handleOrientationChange()
            }
            UIDevice.current.beginGeneratingDeviceOrientationNotifications()
        }

        if config.captureLifecycle {
            lifecycleObserver = NotificationCenter.default.addObserver(
                forName: UIApplication.didBecomeActiveNotification,
                object: nil, queue: .main
            ) { [weak self] _ in
                self?.recordEvent(category: "lifecycle", data: ["action": "did_become_active"])
            }
            NotificationCenter.default.addObserver(
                self, selector: #selector(handleLifecycleEvent(_:)),
                name: UIApplication.willResignActiveNotification,
                object: nil
            )
            NotificationCenter.default.addObserver(
                self, selector: #selector(handleLifecycleEvent(_:)),
                name: UIApplication.didEnterBackgroundNotification,
                object: nil
            )
            NotificationCenter.default.addObserver(
                self, selector: #selector(handleLifecycleEvent(_:)),
                name: UIApplication.willEnterForegroundNotification,
                object: nil
            )
            NotificationCenter.default.addObserver(
                self, selector: #selector(handleLifecycleEvent(_:)),
                name: UIApplication.willTerminateNotification,
                object: nil
            )
        }

        if config.captureSensors {
            startSensorCapture()
        }

        startBatchTimer()
        startSessionTimer()

        recordEvent(category: "system", data: ["action": "capture_started"])
    }

    @objc public func stopCapture() {
        guard isTracking else { return }
        isTracking = false
        flush()

        for gesture in gestureRecognizers {
            targetView?.removeGestureRecognizer(gesture)
        }
        gestureRecognizers.removeAll()

        if let obs = orientationObserver {
            NotificationCenter.default.removeObserver(obs)
            orientationObserver = nil
        }
        if let obs = lifecycleObserver {
            NotificationCenter.default.removeObserver(obs)
            lifecycleObserver = nil
        }
        if let obs = keyboardWillShowObserver {
            NotificationCenter.default.removeObserver(obs)
            keyboardWillShowObserver = nil
        }
        if let obs = keyboardWillHideObserver {
            NotificationCenter.default.removeObserver(obs)
            keyboardWillHideObserver = nil
        }
        UIDevice.current.endGeneratingDeviceOrientationNotifications()

        stopSensorCapture()
        stopBatchTimer()
        stopSessionTimer()
        targetView = nil

        recordEvent(category: "system", data: ["action": "capture_stopped"])
        log("Stopped capture")
    }

    @objc public func handleTouch(_ touch: UITouch, in view: UIView?) {
        guard isTracking && config.captureTouch else { return }
        touchActivity()

        let data = TouchEventData(touch: touch, view: view ?? targetView)

        if touch.phase == .began {
            lastTouchLocation = CGPoint(x: data.locationX, y: data.locationY)
            touchStartTime = touch.timestamp
        }

        if touch.phase == .moved, let last = lastTouchLocation {
            let dx = Double(data.locationX - last.x)
            let dy = Double(data.locationY - last.y)
            let dt = touch.timestamp - touchStartTime
            let distance = sqrt(dx * dx + dy * dy)
            let speed = dt > 0 ? distance / dt : 0

            var touchData = data.toDict()
            touchData["distance"] = distance
            touchData["speed"] = speed
            recordEvent(category: "touch", data: touchData)
            lastTouchLocation = CGPoint(x: data.locationX, y: data.locationY)
        } else {
            recordEvent(category: "touch", data: data.toDict())
        }

        if touch.phase == .ended, let last = lastTouchLocation {
            let dx = Double(data.locationX - last.x)
            let dy = Double(data.locationY - last.y)
            let dt = touch.timestamp - touchStartTime
            let distance = sqrt(dx * dx + dy * dy)
            let speed = dt > 0 ? distance / dt : 0

            if distance > 20 {
                let angle = atan2(dy, dx) * 180 / .pi
                var swipeData: [String: Any] = [
                    "type": "swipe",
                    "direction": directionFromAngle(angle),
                    "distance": distance,
                    "speed": speed,
                    "duration": dt * 1000,
                    "startX": last.x,
                    "startY": last.y,
                    "endX": data.locationX,
                    "endY": data.locationY,
                ]
                recordEvent(category: "gesture", data: swipeData)

                if speed > 500 {
                    swipeData["type"] = "fling"
                    recordEvent(category: "gesture", data: swipeData)
                }
            }
            lastTouchLocation = nil
        }
    }

    @objc public func handleTap(_ gesture: UITapGestureRecognizer) {
        guard isTracking && config.captureGestures else { return }
        touchActivity()
        let data = GestureEventData(type: "tap", gesture: gesture)
        recordEvent(category: "gesture", data: data.toDict())
    }

    @objc public func handleSwipe(_ gesture: UISwipeGestureRecognizer) {
        guard isTracking && config.captureGestures else { return }
        touchActivity()
        let data = SwipeGestureData(type: "swipe", gesture: gesture)
        recordEvent(category: "gesture", data: data.toDict())
    }

    @objc public func handlePan(_ gesture: UIPanGestureRecognizer) {
        guard isTracking && config.captureGestures else { return }
        touchActivity()
        let data = PanGestureData(type: "pan", gesture: gesture)
        recordEvent(category: "gesture", data: data.toDict())

        if gesture.state == .ended {
            let vel = gesture.velocity(in: gesture.view)
            let speed = sqrt(vel.x * vel.x + vel.y * vel.y)
            if speed > 500 {
                let data = PanGestureData(type: "fling", gesture: gesture)
                recordEvent(category: "gesture", data: data.toDict())
            }
        }
    }

    @objc public func handlePinch(_ gesture: UIPinchGestureRecognizer) {
        guard isTracking && config.captureGestures else { return }
        touchActivity()
        let data = PinchGestureData(type: "pinch", gesture: gesture)
        recordEvent(category: "gesture", data: data.toDict())

        if gesture.state == .changed {
            let zoomData = PinchGestureData(type: "zoom", gesture: gesture)
            recordEvent(category: "gesture", data: zoomData.toDict())
        }
    }

    @objc public func handleRotation(_ gesture: UIRotationGestureRecognizer) {
        guard isTracking && config.captureGestures else { return }
        touchActivity()
        let data = RotationGestureData(type: "rotation", gesture: gesture)
        recordEvent(category: "gesture", data: data.toDict())
    }

    @objc public func handleLongPress(_ gesture: UILongPressGestureRecognizer) {
        guard isTracking && config.captureGestures else { return }
        touchActivity()
        let data = LongPressGestureData(type: "long_press", gesture: gesture)
        recordEvent(category: "gesture", data: data.toDict())
    }

    @objc public func handleScreenEdge(_ gesture: UIScreenEdgePanGestureRecognizer) {
        guard isTracking && config.captureGestures else { return }
        touchActivity()
        let data = PanGestureData(type: "screen_edge", gesture: gesture)
        recordEvent(category: "gesture", data: data.toDict())
    }

    @objc public func handleLifecycleEvent(_ notification: Notification) {
        guard isTracking && config.captureLifecycle else { return }
        let name: String = {
            switch notification.name {
            case UIApplication.willResignActiveNotification: return "will_resign_active"
            case UIApplication.didEnterBackgroundNotification: return "did_enter_background"
            case UIApplication.willEnterForegroundNotification: return "will_enter_foreground"
            case UIApplication.willTerminateNotification: return "will_terminate"
            default: return notification.name.rawValue
            }
        }()
        recordEvent(category: "lifecycle", data: ["action": name])

        if notification.name == UIApplication.willTerminateNotification {
            flushSync()
        }
    }

    @objc public func handleOrientationChange() {
        guard isTracking && config.captureOrientation else { return }
        let orientation: String = {
            switch UIDevice.current.orientation {
            case .portrait: return "portrait"
            case .portraitUpsideDown: return "portrait_upside_down"
            case .landscapeLeft: return "landscape_left"
            case .landscapeRight: return "landscape_right"
            case .faceUp: return "face_up"
            case .faceDown: return "face_down"
            default: return "unknown"
            }
        }()
        recordEvent(category: "orientation", data: ["orientation": orientation])
    }

    @objc public func handleKeyboardNotification(_ notification: Notification) {
        guard isTracking && config.captureKeys else { return }
        let isShowing = notification.name == UIResponder.keyboardWillShowNotification
        let data = KeyboardEventData(notification: notification, isKeyDown: isShowing)
        recordEvent(category: "keyboard", data: data.toDict())
    }

    // MARK: - Sensors

    private func startSensorCapture() {
        guard motionManager.isAccelerometerAvailable || motionManager.isGyroAvailable else {
            log("No motion sensors available")
            return
        }

        if motionManager.isAccelerometerAvailable {
            motionManager.accelerometerUpdateInterval = 0.05
            motionManager.startAccelerometerUpdates(to: .main) { [weak self] data, error in
                guard let self = self, let d = data, self.isTracking else { return }
                let event = MotionEventData(
                    type: "accelerometer",
                    x: d.acceleration.x,
                    y: d.acceleration.y,
                    z: d.acceleration.z,
                    timestamp: d.timestamp
                )
                self.recordEvent(category: "sensor", data: event.toDict())
            }
        }

        if motionManager.isGyroAvailable {
            motionManager.gyroUpdateInterval = 0.05
            motionManager.startGyroUpdates(to: .main) { [weak self] data, error in
                guard let self = self, let d = data, self.isTracking else { return }
                let event = MotionEventData(
                    type: "gyroscope",
                    x: d.rotationRate.x,
                    y: d.rotationRate.y,
                    z: d.rotationRate.z,
                    timestamp: d.timestamp
                )
                self.recordEvent(category: "sensor", data: event.toDict())
            }
        }
    }

    private func stopSensorCapture() {
        motionManager.stopAccelerometerUpdates()
        motionManager.stopGyroUpdates()
    }

    // MARK: - Fingerprinting

    @objc public func getDeviceFingerprint() -> [String: Any] {
        if let cached = fingerprintCache { return cached }

        var fp: [String: Any] = [:]
        let device = UIDevice.current

        fp["identifierForVendor"] = device.identifierForVendor?.uuidString ?? ""
        fp["model"] = device.model
        fp["localizedModel"] = device.localizedModel
        fp["systemName"] = device.systemName
        fp["systemVersion"] = device.systemVersion
        fp["userInterfaceIdiom"] = device.userInterfaceIdiom.rawValue
        fp["isMultitaskingSupported"] = device.isMultitaskingSupported

        let screen = UIScreen.main
        fp["screenWidth"] = Int(screen.bounds.width * screen.scale)
        fp["screenHeight"] = Int(screen.bounds.height * screen.scale)
        fp["screenScale"] = Double(screen.scale)
        fp["screenNativeBoundsWidth"] = Int(screen.nativeBounds.width)
        fp["screenNativeBoundsHeight"] = Int(screen.nativeBounds.height)
        fp["screenNativeScale"] = Double(screen.nativeScale)
        fp["screenBrightness"] = Double(screen.brightness)

        let processInfo = ProcessInfo.processInfo
        fp["processName"] = processInfo.processName
        fp["lowPowerMode"] = processInfo.isLowPowerModeEnabled
        fp["physicalMemory"] = processInfo.physicalMemory
        fp["processorCount"] = processInfo.processorCount
        fp["activeProcessorCount"] = processInfo.activeProcessorCount
        fp["operatingSystemVersionString"] = processInfo.operatingSystemVersionString
        fp["thermalState"] = processInfo.thermalState.rawValue

        let locale = Locale.current
        fp["localeIdentifier"] = locale.identifier
        fp["preferredLanguages"] = Locale.preferredLanguages
        fp["currencyCode"] = locale.currencyCode ?? ""
        fp["regionCode"] = locale.regionCode ?? ""

        fp["timezone"] = TimeZone.current.identifier
        fp["timezoneSecondsFromGMT"] = TimeZone.current.secondsFromGMT()

        if let name = UIDevice.current.name {
            fp["deviceName"] = name
        }

        let sysInfo = getSysInfo()
        fp.merge(sysInfo) { current, _ in current }

        let jsonData = try? JSONSerialization.data(withJSONObject: fp, options: [])
        let jsonString = jsonData.flatMap { String(data: $0, encoding: .utf8) } ?? ""
        let hash = sha256(jsonString)
        fp["combinedHash"] = hash

        fingerprintCache = fp
        return fp
    }

    private func getSysInfo() -> [String: Any] {
        var info: [String: Any] = [:]
        var size = 0
        sysctlbyname("hw.machine", nil, &size, nil, 0)
        if size > 0 {
            var machine = [CChar](repeating: 0, count: size)
            sysctlbyname("hw.machine", &machine, &size, nil, 0)
            info["machine"] = String(cString: machine)
        }
        size = 0
        sysctlbyname("hw.model", nil, &size, nil, 0)
        if size > 0 {
            var model = [CChar](repeating: 0, count: size)
            sysctlbyname("hw.model", &model, &size, nil, 0)
            info["hwModel"] = String(cString: model)
        }
        return info
    }

    private func sha256(_ string: String) -> String {
        let data = Data(string.utf8)
        let hash = data.withUnsafeBytes { bytes -> [UInt8] in
            var digest = [UInt8](repeating: 0, count: Int(CC_SHA256_DIGEST_LENGTH))
            CC_SHA256(bytes.baseAddress, CC_LONG(data.count), &digest)
            return digest
        }
        return hash.map { String(format: "%02x", $0) }.joined()
    }

    // MARK: - Session

    @objc public func getSessionData() -> [String: Any] {
        let now = Date().timeIntervalSince1970
        return [
            "sessionId": sessionId,
            "userId": config.userId ?? NSNull(),
            "startTime": sessionStartTs * 1000,
            "eventCount": events.count,
            "duration": (now - sessionStartTs) * 1000,
            "deviceType": "ios",
        ]
    }

    @objc public func getSessionId() -> String {
        return sessionId
    }

    @objc public func getEventCount() -> Int {
        return eventQueue.sync { events.count }
    }

    @objc public func clearEvents() {
        eventQueue.sync { events.removeAll() }
    }

    // MARK: - Submission

    @objc public func submitEvents() throws -> [String: Any] {
        return try submitToEndpoint(endpoint: config.endpoint)
    }

    @objc public func submitEvents(to endpoint: String) throws -> [String: Any] {
        return try submitToEndpoint(endpoint: endpoint)
    }

    private func submitToEndpoint(endpoint: String) throws -> [String: Any] {
        let payload = buildPayload()
        guard let eventsArray = payload["events"] as? [[String: Any]], !eventsArray.isEmpty else {
            throw NSError(domain: "BehaviorTracker", code: 400,
                userInfo: [NSLocalizedDescriptionKey: "No behavioral events recorded"])
        }

        var lastError: Error?
        var attempts = 0
        let maxAttempts = 1 + config.maxRetries

        while attempts < maxAttempts {
            attempts += 1
            do {
                let result = try sendRequest(endpoint: endpoint, payload: payload)
                eventQueue.sync { events.removeAll() }
                retryCount = 0
                log("Submitted \(eventsArray.count) events")
                return result
            } catch {
                lastError = error
                log("Submission failed: \(error.localizedDescription)")
                if attempts < maxAttempts {
                    let delay = config.retryBaseDelaySec * pow(2.0, Double(retryCount))
                    retryCount += 1
                    log("Retrying in \(delay)s (attempt \(attempts)/\(maxAttempts))")
                    Thread.sleep(forTimeInterval: delay)
                }
            }
        }
        throw lastError ?? NSError(domain: "BehaviorTracker", code: 500,
            userInfo: [NSLocalizedDescriptionKey: "Submission failed after \(maxAttempts) attempts"])
    }

    private func sendRequest(endpoint: String, payload: [String: Any]) throws -> [String: Any] {
        guard let url = URL(string: endpoint) else {
            throw NSError(domain: "BehaviorTracker", code: 400,
                userInfo: [NSLocalizedDescriptionKey: "Invalid endpoint URL"])
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: payload, options: [])
        request.timeoutInterval = 10

        let semaphore = DispatchSemaphore(value: 0)
        var result: [String: Any] = [:]
        var requestError: Error?

        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                requestError = error
            } else if let httpResponse = response as? HTTPURLResponse,
                let data = data {
                if httpResponse.statusCode >= 200 && httpResponse.statusCode < 300 {
                    result = (try? JSONSerialization.jsonObject(with: data) as? [String: Any]) ?? [:]
                } else {
                    let body = String(data: data, encoding: .utf8) ?? ""
                    requestError = NSError(domain: "BehaviorTracker", code: httpResponse.statusCode,
                        userInfo: [NSLocalizedDescriptionKey: "HTTP \(httpResponse.statusCode): \(body)"])
                }
            }
            semaphore.signal()
        }
        task.resume()
        semaphore.wait()

        if let error = requestError { throw error }
        return result
    }

    private func buildPayload() -> [String: Any] {
        var payload: [String: Any] = [
            "session_id": sessionId,
            "user_id": config.userId ?? NSNull(),
            "device_type": "ios",
            "duration": (Date().timeIntervalSince1970 - sessionStartTs) * 1000,
        ]
        eventQueue.sync {
            payload["events"] = events
            payload["event_count"] = events.count
        }
        if let fp = fingerprintCache {
            payload["fingerprint"] = fp
        }
        return payload
    }

    @objc public func getEvents() -> [[String: Any]] {
        return eventQueue.sync { events }
    }

    // MARK: - Internal

    private func recordEvent(category: String, data: [String: Any]) {
        var event: [String: Any] = [
            "category": category,
            "session_id": sessionId,
            "ts": Date().timeIntervalSince1970 * 1000,
            "ts_uptime": ProcessInfo.processInfo.systemUptime * 1000,
        ]
        event.merge(data) { current, _ in current }
        eventQueue.sync {
            events.append(event)
            if events.count >= config.batchSize {
                DispatchQueue.global().async { self.flush() }
            }
        }
    }

    private func touchActivity() {
        lastActivityTs = Date().timeIntervalSince1970
    }

    private func flush() {
        eventQueue.sync {
            guard !events.isEmpty else { return }
            let batch = events
            events.removeAll()
            networkQueue.async {
                self.submitBatch(batch)
            }
        }
    }

    private func flushSync() {
        let batch = eventQueue.sync { () -> [[String: Any]] in
            let b = events
            events.removeAll()
            return b
        }
        guard !batch.isEmpty else { return }
        let payload: [String: Any] = [
            "session_id": sessionId,
            "user_id": config.userId ?? NSNull(),
            "device_type": "ios",
            "events": batch,
            "event_count": batch.count,
        ]
        if let data = try? JSONSerialization.data(withJSONObject: payload),
           let url = URL(string: config.endpoint) {
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = data
            URLSession.shared.dataTask(with: request).resume()
        }
    }

    private func submitBatch(_ batch: [[String: Any]]) {
        let payload: [String: Any] = [
            "session_id": sessionId,
            "user_id": config.userId ?? NSNull(),
            "device_type": "ios",
            "events": batch,
            "event_count": batch.count,
        ]

        guard let url = URL(string: config.endpoint),
              let body = try? JSONSerialization.data(withJSONObject: payload) else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = body
        request.timeoutInterval = 5

        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            guard let self = self else { return }
            if let httpResponse = response as? HTTPURLResponse,
               httpResponse.statusCode >= 200 && httpResponse.statusCode < 300 {
                self.retryCount = 0
                self.log("Batch submitted: \(batch.count) events")
            } else {
                self.log("Batch error: \(error?.localizedDescription ?? "unknown")")
                self.eventQueue.sync {
                    self.events.insert(contentsOf: batch, at: 0)
                }
            }
        }.resume()
    }

    private func startBatchTimer() {
        batchTimer = Timer.scheduledTimer(withTimeInterval: config.batchIntervalMs, repeats: true) { [weak self] _ in
            self?.flush()
        }
    }

    private func stopBatchTimer() {
        batchTimer?.invalidate()
        batchTimer = nil
    }

    private func startSessionTimer() {
        sessionTimer = Timer.scheduledTimer(withTimeInterval: config.sessionTimeoutSec / 4, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            let elapsed = Date().timeIntervalSince1970 - self.lastActivityTs
            if elapsed > self.config.sessionTimeoutSec {
                self.log("Session timed out. Rotating session.")
                self.stopCapture()
                self.sessionId = UUID().uuidString
                if let view = self.targetView {
                    self.startCapture(on: view)
                }
            }
        }
    }

    private func stopSessionTimer() {
        sessionTimer?.invalidate()
        sessionTimer = nil
    }

    private func directionFromAngle(_ angle: Double) -> String {
        switch angle {
        case -45..<45: return "right"
        case 45..<135: return "down"
        case -135..<(-45): return "up"
        default: return "left"
        }
    }

    private func log(_ message: String) {
        if config.enableLogging {
            print("[BehaviorTracker] \(message)")
        }
    }
}

// MARK: - Dictionary Convertible

private extension BehaviorTracker.TouchEventData {
    func toDict() -> [String: Any] {
        return [
            "type": type,
            "phase": phase,
            "tapCount": tapCount,
            "force": Double(force),
            "majorRadius": Double(majorRadius),
            "minorRadius": Double(minorRadius),
            "locationX": Double(locationX),
            "locationY": Double(locationY),
            "previousLocationX": Double(previousLocationX),
            "previousLocationY": Double(previousLocationY),
            "timestamp": timestamp,
            "estimationUpdateIndex": estimationUpdateIndex,
            "estimatedPropertiesExpectingUpdates": estimatedPropertiesExpectingUpdates,
            "altitudeAngle": Double(altitudeAngle),
            "azimuthAngle": Double(azimuthAngle),
            "azimuthUnitVectorX": Double(azimuthUnitVectorX),
            "azimuthUnitVectorY": Double(azimuthUnitVectorY),
        ]
    }
}

private extension BehaviorTracker.GestureEventData {
    func toDict() -> [String: Any] {
        return [
            "type": type,
            "state": state,
            "locationX": Double(locationX),
            "locationY": Double(locationY),
            "velocityX": Double(velocityX),
            "velocityY": Double(velocityY),
            "velocity": Double(velocity),
            "translationX": Double(translationX),
            "translationY": Double(translationY),
            "scale": Double(scale),
            "rotation": Double(rotation),
            "direction": direction ?? NSNull(),
            "numberOfTouches": numberOfTouches,
            "durationMs": durationMs,
        ]
    }
}

private extension BehaviorTracker.MotionEventData {
    func toDict() -> [String: Any] {
        return [
            "type": type,
            "x": x,
            "y": y,
            "z": z,
            "timestamp": timestamp,
        ]
    }
}

private extension BehaviorTracker.KeyboardEventData {
    func toDict() -> [String: Any] {
        return [
            "type": type,
            "characters": characters,
            "charactersIgnoringModifiers": charactersIgnoringModifiers,
            "modifierFlags": modifierFlags,
            "keyCode": keyCode,
            "isRepeat": isRepeat,
        ]
    }
}
