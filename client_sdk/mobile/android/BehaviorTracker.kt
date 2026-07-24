package com.behavioral.biometric.sdk

import android.app.Activity
import android.app.Application
import android.content.Context
import android.content.res.Configuration
import android.graphics.Point
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Build
import android.os.Bundle
import android.os.SystemClock
import android.provider.Settings
import android.util.DisplayMetrics
import android.view.InputDevice
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.VelocityTracker
import android.view.View
import android.view.WindowManager
import java.io.BufferedReader
import java.io.InputStreamReader
import java.lang.ref.WeakReference
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.UUID
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import kotlin.math.abs
import kotlin.math.atan2
import kotlin.math.sqrt
import kotlin.math.roundToLong
import org.json.JSONArray
import org.json.JSONObject

class BehaviorTracker private constructor(
    private val context: Context,
    private val config: Config
) {
    data class Config(
        val userId: String? = null,
        val endpoint: String = "/api/events",
        val batchIntervalMs: Long = 5000,
        val batchSize: Int = 50,
        val captureTouch: Boolean = true,
        val captureMotion: Boolean = true,
        val captureKeys: Boolean = true,
        val captureSensors: Boolean = true,
        val captureOrientation: Boolean = true,
        val captureLifecycle: Boolean = true,
        val sessionTimeoutMs: Long = 1800000,
        val maxRetries: Int = 3,
        val retryBaseDelayMs: Long = 1000,
        val enableLogging: Boolean = false,
        val gestureVelocityUnits: Int = 1000,
        val sensorSamplingPeriodUs: Int = SensorManager.SENSOR_DELAY_GAME,
    )

    data class KeyEventData(
        val type: String,
        val keyCode: Int,
        val keyChar: String,
        val action: Int,
        val eventTime: Long,
        val downTime: Long,
        val repeatCount: Int,
        val metaState: Int,
        val deviceId: Int,
        val isLongPress: Boolean,
    )

    data class TouchEventData(
        val type: String,
        val pointerId: Int,
        val action: Int,
        val x: Float,
        val y: Float,
        val pressure: Float,
        val size: Float,
        val orientation: Float,
        val eventTime: Long,
        val downTime: Long,
        val deviceId: Int,
        val edgeFlags: Int,
        val toolType: Int,
        val axisX: Float,
        val axisY: Float,
        val axisPressure: Float,
        val axisSize: Float,
    )

    data class GestureEventData(
        val type: String,
        val direction: String?,
        val velocityX: Float,
        val velocityY: Float,
        val velocity: Float,
        val distanceX: Float,
        val distanceY: Float,
        val distance: Float,
        val durationMs: Long,
        val scale: Float?,
        val focusX: Float?,
        val focusY: Float?,
        val span: Float?,
        val rotation: Float?,
    )

    data class MotionEventData(
        val type: String,
        val x: Float,
        val y: Float,
        val z: Float,
        val accuracy: Int,
        val timestamp: Long,
        val sensorType: Int,
        val sensorName: String,
    )

    data class SessionData(
        val sessionId: String,
        val userId: String?,
        val startTime: Long,
        val eventCount: Int,
        val duration: Long,
        val deviceType: String = "android",
    )

    private var sessionId: String = UUID.randomUUID().toString()
    private val events = mutableListOf<JSONObject>()
    private val isTracking = AtomicBoolean(false)
    private val retryCount = AtomicInteger(0)
    private var lastActivityTs: Long = System.currentTimeMillis()
    private var sessionStartTs: Long = System.currentTimeMillis()
    private var batchTimer: Thread? = null
    private var sessionMonitor: Thread? = null

    private var sensorManager: SensorManager? = null
    private var accelerometer: Sensor? = null
    private var gyroscope: Sensor? = null
    private var sensorEventListener: SensorEventListener? = null

    private var velocityTracker: VelocityTracker? = null
    private var gestureStartX: Float = 0f
    private var gestureStartY: Float = 0f
    private var gestureStartTs: Long = 0L
    private var lastPinchSpan: Float = -1f
    private var currentScale: Float = 1f
    private var lastRotation: Float = 0f
    private var currentRotation: Float = 0f

    private var fingerprint: JSONObject? = null
    private var lifecycleCallback: Application.ActivityLifecycleCallbacks? = null
    private val executor = Executors.newSingleThreadScheduledExecutor()

    private val lifecycleListener = object : Application.ActivityLifecycleCallbacks {
        override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {
            recordEvent("lifecycle", "activity_created", activity.localClassName)
        }
        override fun onActivityStarted(activity: Activity) {
            recordEvent("lifecycle", "activity_started", activity.localClassName)
        }
        override fun onActivityResumed(activity: Activity) {
            recordEvent("lifecycle", "activity_resumed", activity.localClassName)
        }
        override fun onActivityPaused(activity: Activity) {
            recordEvent("lifecycle", "activity_paused", activity.localClassName)
        }
        override fun onActivityStopped(activity: Activity) {
            recordEvent("lifecycle", "activity_stopped", activity.localClassName)
        }
        override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) {}
        override fun onActivityDestroyed(activity: Activity) {
            recordEvent("lifecycle", "activity_destroyed", activity.localClassName)
        }
    }

    fun getTouchEventListener(): View.OnTouchListener {
        return View.OnTouchListener { _, event ->
            if (isTracking.get() && config.captureTouch) {
                handleTouchEvent(event)
            }
            false
        }
    }

    fun handleTouchEvent(event: MotionEvent) {
        touchActivity()
        val pointerIndex = event.actionIndex
        val pointerId = event.getPointerId(pointerIndex)
        val action = event.actionMasked

        val touchEvent = TouchEventData(
            type = when (action) {
                MotionEvent.ACTION_DOWN, MotionEvent.ACTION_POINTER_DOWN -> "touch_down"
                MotionEvent.ACTION_MOVE -> "touch_move"
                MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> "touch_up"
                MotionEvent.ACTION_CANCEL -> "touch_cancel"
                else -> "touch_other"
            },
            pointerId = pointerId,
            action = action,
            x = event.getX(pointerIndex),
            y = event.getY(pointerIndex),
            pressure = event.getPressure(pointerIndex),
            size = event.getSize(pointerIndex),
            orientation = event.getOrientation(pointerIndex),
            eventTime = event.eventTime,
            downTime = event.downTime,
            deviceId = event.deviceId,
            edgeFlags = event.edgeFlags,
            toolType = event.getToolType(pointerIndex),
            axisX = event.getAxisValue(MotionEvent.AXIS_X, pointerIndex),
            axisY = event.getAxisValue(MotionEvent.AXIS_Y, pointerIndex),
            axisPressure = event.getAxisValue(MotionEvent.AXIS_PRESSURE, pointerIndex),
            axisSize = event.getAxisValue(MotionEvent.AXIS_SIZE, pointerIndex),
        )
        recordEvent("touch", toJson(touchEvent))

        when (action) {
            MotionEvent.ACTION_DOWN, MotionEvent.ACTION_POINTER_DOWN -> {
                gestureStartX = event.getX(pointerIndex)
                gestureStartY = event.getY(pointerIndex)
                gestureStartTs = System.currentTimeMillis()
                lastPinchSpan = -1f
                currentScale = 1f
                velocityTracker?.clear()
                velocityTracker = VelocityTracker.obtain()
                velocityTracker?.addMovement(event)
            }
            MotionEvent.ACTION_MOVE -> {
                velocityTracker?.addMovement(event)
                if (event.pointerCount >= 2) {
                    detectPinchZoom(event)
                    detectRotation(event)
                }
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> {
                velocityTracker?.computeCurrentVelocity(config.gestureVelocityUnits)
                val vx = velocityTracker?.xVelocity ?: 0f
                val vy = velocityTracker?.yVelocity ?: 0f
                detectSwipeGesture(event.getX(pointerIndex), event.getY(pointerIndex), vx, vy)
                velocityTracker?.recycle()
                velocityTracker = null
            }
        }
    }

    fun handleKeyEvent(event: KeyEvent): Boolean {
        if (!isTracking.get() || !config.captureKeys) return false
        touchActivity()

        val keyData = KeyEventData(
            type = if (event.action == KeyEvent.ACTION_DOWN) "key_down" else "key_up",
            keyCode = event.keyCode,
            keyChar = event.unicodeChar.toChar().toString(),
            action = event.action,
            eventTime = event.eventTime,
            downTime = event.downTime,
            repeatCount = event.repeatCount,
            metaState = event.metaState,
            deviceId = event.deviceId,
            isLongPress = event.isLongPress,
        )
        recordEvent("keyboard", toJson(keyData))
        return false
    }

    private fun detectSwipeGesture(endX: Float, endY: Float, vx: Float, vy: Float) {
        val dx = endX - gestureStartX
        val dy = endY - gestureStartY
        val distance = sqrt((dx * dx + dy * dy).toDouble()).toFloat()
        val duration = System.currentTimeMillis() - gestureStartTs

        if (distance < 30) return

        val angle = Math.toDegrees(atan2(dy.toDouble(), dx.toDouble())).toFloat()
        val direction = when {
            angle in -45f..45f -> "right"
            angle in 45f..135f -> "down"
            angle in -135f..-45f -> "up"
            else -> "left"
        }

        val gesture = GestureEventData(
            type = "swipe",
            direction = direction,
            velocityX = vx,
            velocityY = vy,
            velocity = sqrt((vx * vx + vy * vy).toDouble()).toFloat(),
            distanceX = dx,
            distanceY = dy,
            distance = distance,
            durationMs = duration,
            scale = null,
            focusX = null,
            focusY = null,
            span = null,
            rotation = null,
        )
        recordEvent("gesture", toJson(gesture))

        if (vx > 2000 || vy > 2000 || vx < -2000 || vy < -2000) {
            val fling = gesture.copy(type = "fling", velocity = sqrt((vx * vx + vy * vy).toDouble()).toFloat())
            recordEvent("gesture", toJson(fling))
        }
    }

    private fun detectPinchZoom(event: MotionEvent) {
        val p0x = event.getX(0)
        val p0y = event.getY(0)
        val p1x = event.getX(1)
        val p1y = event.getY(1)
        val span = sqrt(((p1x - p0x) * (p1x - p0x) + (p1y - p0y) * (p1y - p0y)).toDouble()).toFloat()

        if (lastPinchSpan > 0) {
            currentScale = span / lastPinchSpan
            val focusX = (p0x + p1x) / 2f
            val focusY = (p0y + p1y) / 2f

            val pinch = GestureEventData(
                type = "pinch",
                direction = if (currentScale > 1f) "out" else "in",
                velocityX = 0f,
                velocityY = 0f,
                velocity = 0f,
                distanceX = 0f,
                distanceY = 0f,
                distance = 0f,
                durationMs = 0,
                scale = currentScale,
                focusX = focusX,
                focusY = focusY,
                span = span,
                rotation = null,
            )
            recordEvent("gesture", toJson(pinch))

            val focus = GestureEventData(
                type = "zoom",
                direction = null,
                velocityX = 0f,
                velocityY = 0f,
                velocity = 0f,
                distanceX = 0f,
                distanceY = 0f,
                distance = 0f,
                durationMs = 0,
                scale = currentScale,
                focusX = focusX,
                focusY = focusY,
                span = span,
                rotation = null,
            )
            recordEvent("gesture", toJson(focus))
        }
        lastPinchSpan = span
    }

    private fun detectRotation(event: MotionEvent) {
        val dx = event.getX(1) - event.getX(0)
        val dy = event.getY(1) - event.getY(0)
        val angle = Math.toDegrees(atan2(dy.toDouble(), dx.toDouble())).toFloat()
        currentRotation = angle

        if (lastRotation != 0f && abs(currentRotation - lastRotation) > 5f) {
            val rot = GestureEventData(
                type = "rotation",
                direction = if (currentRotation > lastRotation) "clockwise" else "counterclockwise",
                velocityX = 0f,
                velocityY = 0f,
                velocity = 0f,
                distanceX = 0f,
                distanceY = 0f,
                distance = 0f,
                durationMs = 0,
                scale = null,
                focusX = null,
                focusY = null,
                span = null,
                rotation = currentRotation - lastRotation,
            )
            recordEvent("gesture", toJson(rot))
        }
        lastRotation = currentRotation
    }

    fun startCapture(activity: Activity) {
        if (isTracking.getAndSet(true)) return
        log("Starting capture, session: $sessionId")
        sessionStartTs = System.currentTimeMillis()
        lastActivityTs = sessionStartTs
        events.clear()

        if (config.captureLifecycle) {
            val app = context.applicationContext as Application
            lifecycleCallback = lifecycleListener
            app.registerActivityLifecycleCallbacks(lifecycleCallback)
        }

        if (config.captureSensors) {
            startSensorCapture()
        }

        startBatchTimer()
        startSessionMonitor()

        recordEvent("system", "capture_started", "Tracking initialized")
    }

    fun stopCapture() {
        if (!isTracking.getAndSet(false)) return
        flush()
        stopSensorCapture()
        stopBatchTimer()
        stopSessionMonitor()

        if (lifecycleCallback != null) {
            val app = context.applicationContext as Application
            app.unregisterActivityLifecycleCallbacks(lifecycleCallback)
            lifecycleCallback = null
        }

        recordEvent("system", "capture_stopped", "Tracking terminated")
        log("Stopped capture")
    }

    private fun startSensorCapture() {
        sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager?.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        gyroscope = sensorManager?.getDefaultSensor(Sensor.TYPE_GYROSCOPE)

        sensorEventListener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent) {
                if (!isTracking.get()) return
                val sensorData = MotionEventData(
                    type = if (event.sensor.type == Sensor.TYPE_ACCELEROMETER) "accelerometer" else "gyroscope",
                    x = event.values[0],
                    y = event.values[1],
                    z = event.values[2],
                    accuracy = event.accuracy,
                    timestamp = event.timestamp,
                    sensorType = event.sensor.type,
                    sensorName = event.sensor.name,
                )
                recordEvent("sensor", toJson(sensorData))
            }

            override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {
                if (!isTracking.get()) return
                val meta = JSONObject()
                meta.put("type", "sensor_accuracy")
                meta.put("sensor", sensor.name)
                meta.put("accuracy", accuracy)
                meta.put("timestamp", System.currentTimeMillis())
                recordEvent("sensor", meta)
            }
        }

        accelerometer?.let {
            sensorManager?.registerListener(sensorEventListener, it, config.sensorSamplingPeriodUs)
        }
        gyroscope?.let {
            sensorManager?.registerListener(sensorEventListener, it, config.sensorSamplingPeriodUs)
        }
    }

    private fun stopSensorCapture() {
        sensorEventListener?.let { sensorManager?.unregisterListener(it) }
        sensorEventListener = null
        sensorManager = null
    }

    fun onConfigurationChanged(newConfig: Configuration) {
        if (!isTracking.get() || !config.captureOrientation) return
        val orient = JSONObject()
        orient.put("type", "orientation_change")
        orient.put("orientation", when (newConfig.orientation) {
            Configuration.ORIENTATION_LANDSCAPE -> "landscape"
            Configuration.ORIENTATION_PORTRAIT -> "portrait"
            Configuration.ORIENTATION_SQUARE -> "square"
            else -> "undefined"
        })
        orient.put("screenLayout", newConfig.screenLayout)
        orient.put("timestamp", System.currentTimeMillis())
        recordEvent("orientation", orient)
    }

    private fun recordEvent(category: String, data: JSONObject) {
        val event = JSONObject()
        event.put("category", category)
        event.put("session_id", sessionId)
        event.put("ts", System.currentTimeMillis())
        event.put("ts_uptime", SystemClock.uptimeMillis())
        event.put("data", data)
        synchronized(events) { events.add(event) }
        if (events.size >= config.batchSize) {
            flush()
        }
    }

    private fun recordEvent(category: String, action: String, detail: String) {
        val data = JSONObject()
        data.put("action", action)
        data.put("detail", detail)
        recordEvent(category, data)
    }

    private fun touchActivity() {
        lastActivityTs = System.currentTimeMillis()
    }

    fun getDeviceFingerprint(): JSONObject {
        if (fingerprint != null) return fingerprint!!

        val fp = JSONObject()
        try {
            fp.put("deviceId", Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID))
            fp.put("model", Build.MODEL)
            fp.put("manufacturer", Build.MANUFACTURER)
            fp.put("brand", Build.BRAND)
            fp.put("product", Build.PRODUCT)
            fp.put("device", Build.DEVICE)
            fp.put("hardware", Build.HARDWARE)
            fp.put("board", Build.BOARD)
            fp.put("display", Build.DISPLAY)
            fp.put("fingerprintTag", Build.FINGERPRINT)
            fp.put("sdkInt", Build.VERSION.SDK_INT)
            fp.put("release", Build.VERSION.RELEASE)
            fp.put("codename", Build.VERSION.CODENAME)
            fp.put("buildType", Build.TYPE)
            fp.put("buildTags", Build.TAGS)
            fp.put("buildId", Build.ID)
            fp.put("buildTime", Build.TIME)

            val wm = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
            val dMetrics = DisplayMetrics()
            wm.defaultDisplay.getRealMetrics(dMetrics)
            val size = Point()
            wm.defaultDisplay.getRealSize(size)
            fp.put("screenWidth", size.x)
            fp.put("screenHeight", size.y)
            fp.put("density", dMetrics.density)
            fp.put("densityDpi", dMetrics.densityDpi)
            fp.put("scaledDensity", dMetrics.scaledDensity)
            fp.put("xdpi", dMetrics.xdpi.toDouble())
            fp.put("ydpi", dMetrics.ydpi.toDouble())
            fp.put("refreshRate", wm.defaultDisplay.refreshRate.toDouble())

            val tm = context.getSystemService(Context.TELEPHONY_SERVICE) as? android.telephony.TelephonyManager
            try {
                fp.put("networkCountryIso", tm?.networkCountryIso ?: "")
                fp.put("simCountryIso", tm?.simCountryIso ?: "")
            } catch (_: SecurityException) {}

            fp.put("timezone", java.util.TimeZone.getDefault().id)
            fp.put("locale", java.util.Locale.getDefault().toString())
            fp.put("displayLanguage", java.util.Locale.getDefault().displayLanguage)

            fp.put("totalRam", getTotalRam())
            fp.put("cpuInfo", getCpuInfo())

            val sb = StringBuilder()
            fp.keys().forEachRemaining { key ->
                sb.append(key).append("=").append(fp.get(key)).append("|")
            }
            val digest = MessageDigest.getInstance("SHA-256")
            val hash = digest.digest(sb.toString().toByteArray())
            fp.put("combinedHash", hash.joinToString("") { "%02x".format(it) })
        } catch (e: Exception) {
            log("Fingerprint error: ${e.message}")
        }

        fingerprint = fp
        return fp
    }

    private fun getTotalRam(): Long {
        try {
            val reader = BufferedReader(InputStreamReader(Runtime.getRuntime().exec("cat /proc/meminfo").inputStream))
            var line = reader.readLine()
            reader.close()
            if (line != null) {
                line = line.replace(Regex("\\D+"), "").trim()
                return line.toLongOrNull() ?: 0L
            }
        } catch (_: Exception) {}
        return 0L
    }

    private fun getCpuInfo(): String {
        try {
            val reader = BufferedReader(InputStreamReader(Runtime.getRuntime().exec("cat /proc/cpuinfo").inputStream))
            val sb = StringBuilder()
            var line = reader.readLine()
            while (line != null) {
                sb.append(line).append("\n")
                line = reader.readLine()
            }
            reader.close()
            val text = sb.toString()
            val hardware = Regex("Hardware[\\s]*:[\\s]*(.*)").find(text)
            val processor = Regex("Processor[\\s]*:[\\s]*(.*)").find(text)
            return buildString {
                hardware?.let { append("Hardware: ${it.groupValues[1]}; ") }
                processor?.let { append("Processor: ${it.groupValues[1]}") }
                if (isEmpty()) append(text.take(256))
            }
        } catch (_: Exception) {
            return Build.CPU_ABI + ", " + Build.CPU_ABI2
        }
    }

    fun getSessionData(): SessionData {
        return SessionData(
            sessionId = sessionId,
            userId = config.userId,
            startTime = sessionStartTs,
            eventCount = events.size,
            duration = System.currentTimeMillis() - sessionStartTs,
        )
    }

    fun submitEvents(): JSONObject {
        return submitToEndpoint(config.endpoint)
    }

    fun submitEvents(endpoint: String): JSONObject {
        return submitToEndpoint(endpoint)
    }

    private fun submitToEndpoint(endpoint: String): JSONObject {
        val payload = buildPayload()
        if (payload.getJSONArray("events").length() == 0) {
            throw IllegalStateException("No behavioral events recorded")
        }

        try {
            val url = URL(endpoint)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.doOutput = true
            conn.connectTimeout = 10000
            conn.readTimeout = 10000

            conn.outputStream.write(payload.toString().toByteArray())
            conn.outputStream.flush()
            conn.outputStream.close()

            val code = conn.responseCode
            val responseStr = if (code in 200..299) {
                BufferedReader(InputStreamReader(conn.inputStream)).readText()
            } else {
                BufferedReader(InputStreamReader(conn.errorStream)).readText()
            }
            conn.disconnect()

            if (code !in 200..299) {
                throw RuntimeException("HTTP $code: $responseStr")
            }

            synchronized(events) { events.clear() }
            retryCount.set(0)
            log("Submitted ${payload.getJSONArray("events").length()} events")
            return JSONObject(responseStr)
        } catch (e: Exception) {
            log("Submission failed: ${e.message}")
            if (retryCount.get() < config.maxRetries) {
                val delay = config.retryBaseDelayMs * (1L shl retryCount.get())
                retryCount.incrementAndGet()
                log("Retrying in ${delay}ms (attempt ${retryCount.get()}/${config.maxRetries})")
                Thread.sleep(delay)
                return submitToEndpoint(endpoint)
            } else {
                log("Max retries reached")
                throw e
            }
        }
    }

    private fun buildPayload(): JSONObject {
        val payload = JSONObject()
        payload.put("session_id", sessionId)
        payload.put("user_id", config.userId ?: JSONObject.NULL)
        payload.put("device_type", "android")
        synchronized(events) {
            val arr = JSONArray()
            events.forEach { arr.put(it) }
            payload.put("events", arr)
            payload.put("event_count", events.size)
        }
        payload.put("duration", System.currentTimeMillis() - sessionStartTs)
        fingerprint?.let { payload.put("fingerprint", it) }
        return payload
    }

    fun getEvents(): List<JSONObject> {
        synchronized(events) { return events.toList() }
    }

    fun clearEvents() {
        synchronized(events) { events.clear() }
    }

    fun getSessionId(): String = sessionId

    fun getEventCount(): Int {
        synchronized(events) { return events.size }
    }

    private fun flush() {
        synchronized(events) {
            if (events.isEmpty()) return
            val copy = events.toList()
            events.clear()
            executor.submit {
                try {
                    submitBatch(copy)
                } catch (e: Exception) {
                    log("Batch flush error: ${e.message}")
                    synchronized(events) { events.addAll(0, copy) }
                }
            }
        }
    }

    private fun submitBatch(batch: List<JSONObject>) {
        val payload = JSONObject()
        payload.put("session_id", sessionId)
        payload.put("user_id", config.userId ?: JSONObject.NULL)
        payload.put("device_type", "android")
        val arr = JSONArray()
        batch.forEach { arr.put(it) }
        payload.put("events", arr)
        payload.put("event_count", batch.size)
        fingerprint?.let { payload.put("fingerprint", it) }

        try {
            val url = URL(config.endpoint)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.doOutput = true
            conn.connectTimeout = 5000
            conn.readTimeout = 5000
            conn.outputStream.write(payload.toString().toByteArray())
            conn.outputStream.flush()
            conn.outputStream.close()
            val code = conn.responseCode
            conn.disconnect()
            if (code in 200..299) {
                retryCount.set(0)
                log("Batch submitted: ${batch.size} events")
            } else {
                throw RuntimeException("HTTP $code")
            }
        } catch (e: Exception) {
            log("Batch error: ${e.message}")
            synchronized(events) { events.addAll(0, batch) }
        }
    }

    private fun startBatchTimer() {
        batchTimer = Thread {
            while (isTracking.get()) {
                try {
                    Thread.sleep(config.batchIntervalMs)
                    flush()
                } catch (_: InterruptedException) {
                    break
                }
            }
        }.apply { isDaemon = true; start() }
    }

    private fun stopBatchTimer() {
        batchTimer?.interrupt()
        batchTimer = null
    }

    private fun startSessionMonitor() {
        sessionMonitor = Thread {
            while (isTracking.get()) {
                try {
                    Thread.sleep(config.sessionTimeoutMs / 4)
                    val elapsed = System.currentTimeMillis() - lastActivityTs
                    if (elapsed > config.sessionTimeoutMs) {
                        log("Session timed out after inactivity. Rotating session.")
                        stopCapture()
                        sessionId = UUID.randomUUID().toString()
                        startCapture(WeakReference(null).get() ?: return@Thread)
                    }
                } catch (_: InterruptedException) {
                    break
                }
            }
        }.apply { isDaemon = true; start() }
    }

    private fun stopSessionMonitor() {
        sessionMonitor?.interrupt()
        sessionMonitor = null
    }

    private fun toJson(obj: Any): JSONObject {
        val json = JSONObject()
        val fields = obj::class.java.declaredFields
        for (field in fields) {
            field.isAccessible = true
            try {
                json.put(field.name, field.get(obj)?.let {
                    when (it) {
                        is Float -> it.toDouble()
                        is Long -> it
                        is Int -> it
                        is Boolean -> it
                        is String -> it
                        else -> it.toString()
                    }
                } ?: JSONObject.NULL)
            } catch (_: Exception) {}
        }
        return json
    }

    private fun log(msg: String) {
        if (config.enableLogging) {
            android.util.Log.d("BehaviorTracker", msg)
        }
    }

    companion object {
        @Volatile
        private var instance: BehaviorTracker? = null

        fun getInstance(context: Context, config: Config = Config()): BehaviorTracker {
            return instance ?: synchronized(this) {
                instance ?: BehaviorTracker(context.applicationContext, config).also { instance = it }
            }
        }

        fun resetInstance() {
            synchronized(this) {
                instance?.stopCapture()
                instance = null
            }
        }
    }
}
