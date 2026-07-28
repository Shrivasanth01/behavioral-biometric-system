/**
 * BehaviorTracker - Production Web SDK for Behavioral Biometrics
 * Captures keyboard, mouse, touch, scroll, focus, clipboard, resize,
 * visibility, and navigation events with device fingerprinting.
 */
class BehavioralTracker {
  constructor(config = {}) {
    this.config = Object.assign({
      userId: null,
      sessionId: null,
      endpoint: '/api/v1/telemetry/batch',
      batchInterval: 5000,
      batchSize: 50,
      throttleMousemove: 50,
      throttleScroll: 100,
      captureKeys: true,
      captureMouse: true,
      captureScroll: true,
      captureFocus: true,
      captureTouch: true,
      captureClipboard: true,
      captureResize: true,
      captureVisibility: true,
      captureNavigation: true,
      fingerprint: true,
      enableLogging: false,
      sessionTimeout: 1800000,
      maxRetries: 3,
      retryBaseDelay: 1000,
    }, config);

    this.sessionId = this.config.sessionId || this._generateId('sess_');
    this.userId = this.config.userId;
    this.events = [];
    this._listeners = [];
    this._isTracking = false;
    this._batchTimer = null;
    this._lastActivity = Date.now();
    this._lastMousePos = null;
    this._lastMouseTime = 0;
    this._frozen = false;
    this._retryCount = 0;
    this._fingerprint = null;
    this._onEventCallbacks = [];

    this._bound = {
      handleKeyDown: this._handleKeyDown.bind(this),
      handleKeyUp: this._handleKeyUp.bind(this),
      handleMouseMove: this._handleMouseMove.bind(this),
      handleMouseDown: this._handleMouseDown.bind(this),
      handleMouseUp: this._handleMouseUp.bind(this),
      handleClick: this._handleClick.bind(this),
      handleContextMenu: this._handleContextMenu.bind(this),
      handleDblClick: this._handleDblClick.bind(this),
      handleTouchStart: this._handleTouchStart.bind(this),
      handleTouchMove: this._handleTouchMove.bind(this),
      handleTouchEnd: this._handleTouchEnd.bind(this),
      handleScroll: this._handleScroll.bind(this),
      handleWheel: this._handleWheel.bind(this),
      handleFocus: this._handleFocus.bind(this),
      handleBlur: this._handleBlur.bind(this),
      handleFocusIn: this._handleFocusIn.bind(this),
      handleFocusOut: this._handleFocusOut.bind(this),
      handleCopy: this._handleClipboard.bind(this, 'copy'),
      handleCut: this._handleClipboard.bind(this, 'cut'),
      handlePaste: this._handleClipboard.bind(this, 'paste'),
      handleResize: this._handleResize.bind(this),
      handleVisibilityChange: this._handleVisibilityChange.bind(this),
      handlePopState: this._handlePopState.bind(this),
      handleBeforeUnload: this._handleBeforeUnload.bind(this),
    };
  }

  _log(...args) {
    if (this.config.enableLogging) {
      console.log('[BehaviorTracker]', ...args);
    }
  }

  _warn(...args) {
    if (this.config.enableLogging) {
      console.warn('[BehaviorTracker]', ...args);
    }
  }

  _generateId(prefix) {
    const arr = new Uint8Array(12);
    crypto.getRandomValues(arr);
    return prefix + Array.from(arr, b => b.toString(16).padStart(2, '0')).join('');
  }

  _now() {
    return performance.now();
  }

  _timestamp() {
    return Date.now();
  }

  _touchActivity() {
    this._lastActivity = this._timestamp();
    if (this._frozen) {
      this._frozen = false;
      this._log('Session resumed from frozen state');
    }
  }

  _addEvent(event) {
    this._touchActivity();
    event.session_id = this.sessionId;
    event.ts = this._timestamp();
    event.ts_perf = this._now();
    event.page_url = window.location.href;
    this.events.push(event);
    this._onEventCallbacks.forEach(cb => cb(event));
    if (this.events.length >= this.config.batchSize) {
      this._flush();
    }
  }

  _addListener(target, type, handler, options) {
    const opts = options || false;
    target.addEventListener(type, handler, opts);
    this._listeners.push({ target, type, handler, opts });
  }

  _removeListeners() {
    for (const { target, type, handler, opts } of this._listeners) {
      target.removeEventListener(type, handler, opts);
    }
    this._listeners = [];
  }

  // --- Keyboard ---
  _handleKeyDown(e) {
    if (!this.config.captureKeys) return;
    this._addEvent({
      type: 'keydown',
      key: e.key,
      code: e.code,
      location: e.location,
      repeat: e.repeat,
      alt: e.altKey,
      ctrl: e.ctrlKey,
      shift: e.shiftKey,
      meta: e.metaKey,
    });
  }

  _handleKeyUp(e) {
    if (!this.config.captureKeys) return;
    const dt = this._now();
    this._addEvent({
      type: 'keyup',
      key: e.key,
      code: e.code,
      location: e.location,
      alt: e.altKey,
      ctrl: e.ctrlKey,
      shift: e.shiftKey,
      meta: e.metaKey,
    });
  }

  // --- Mouse ---
  _handleMouseMove(e) {
    if (!this.config.captureMouse) return;
    const now = this._now();
    if (now - this._lastMouseTime < this.config.throttleMousemove) return;
    this._lastMouseTime = now;
    const pos = { x: e.clientX, y: e.clientY };
    let speed = 0;
    let acceleration = 0;
    if (this._lastMousePos) {
      const dx = pos.x - this._lastMousePos.x;
      const dy = pos.y - this._lastMousePos.y;
      speed = Math.sqrt(dx * dx + dy * dy) / ((now - this._lastMouseTime) || 1);
      acceleration = speed - (this._lastMousePos.speed || 0);
    }
    this._lastMousePos = { ...pos, speed, time: now };
    this._addEvent({
      type: 'mousemove',
      x: e.clientX,
      y: e.clientY,
      screenX: e.screenX,
      screenY: e.screenY,
      target: e.target ? e.target.tagName : null,
      speed: Math.round(speed * 100) / 100,
      acceleration: Math.round(acceleration * 100) / 100,
    });
  }

  _handleMouseDown(e) {
    if (!this.config.captureMouse) return;
    this._addEvent({
      type: 'mousedown',
      x: e.clientX,
      y: e.clientY,
      button: e.button,
      buttons: e.buttons,
      target: e.target ? e.target.tagName : null,
    });
  }

  _handleMouseUp(e) {
    if (!this.config.captureMouse) return;
    this._addEvent({
      type: 'mouseup',
      x: e.clientX,
      y: e.clientY,
      button: e.button,
      buttons: e.buttons,
      target: e.target ? e.target.tagName : null,
    });
  }

  _handleClick(e) {
    if (!this.config.captureMouse) return;
    this._addEvent({
      type: 'click',
      x: e.clientX,
      y: e.clientY,
      button: e.button,
      target: e.target ? e.target.tagName : null,
    });
  }

  _handleContextMenu(e) {
    if (!this.config.captureMouse) return;
    this._addEvent({
      type: 'contextmenu',
      x: e.clientX,
      y: e.clientY,
      target: e.target ? e.target.tagName : null,
    });
  }

  _handleDblClick(e) {
    if (!this.config.captureMouse) return;
    this._addEvent({
      type: 'dblclick',
      x: e.clientX,
      y: e.clientY,
      target: e.target ? e.target.tagName : null,
    });
  }

  // --- Touch ---
  _handleTouchStart(e) {
    if (!this.config.captureTouch) return;
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      this._addEvent({
        type: 'touchstart',
        touchId: t.identifier,
        x: t.clientX,
        y: t.clientY,
        radiusX: t.radiusX || 0,
        radiusY: t.radiusY || 0,
        rotationAngle: t.rotationAngle || 0,
        force: t.force || 0,
        target: e.target ? e.target.tagName : null,
      });
    }
  }

  _handleTouchMove(e) {
    if (!this.config.captureTouch) return;
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      this._addEvent({
        type: 'touchmove',
        touchId: t.identifier,
        x: t.clientX,
        y: t.clientY,
        radiusX: t.radiusX || 0,
        radiusY: t.radiusY || 0,
        rotationAngle: t.rotationAngle || 0,
        force: t.force || 0,
      });
    }
  }

  _handleTouchEnd(e) {
    if (!this.config.captureTouch) return;
    for (let i = 0; i < e.changedTouches.length; i++) {
      const t = e.changedTouches[i];
      this._addEvent({
        type: 'touchend',
        touchId: t.identifier,
        x: t.clientX,
        y: t.clientY,
        force: t.force || 0,
      });
    }
  }

  // --- Scroll ---
  _handleScroll(e) {
    if (!this.config.captureScroll) return;
    if (this._scrollThrottled) return;
    this._scrollThrottled = true;
    setTimeout(() => { this._scrollThrottled = false; }, this.config.throttleScroll);
    const target = e.target;
    const el = target === document ? document.documentElement : target;
    this._addEvent({
      type: 'scroll',
      scrollX: (el && el.scrollLeft) || window.scrollX || window.pageXOffset,
      scrollY: (el && el.scrollTop) || window.scrollY || window.pageYOffset,
      target: target ? (target.tagName || 'document') : null,
    });
  }

  _handleWheel(e) {
    if (!this.config.captureScroll) return;
    this._addEvent({
      type: 'wheel',
      deltaX: e.deltaX,
      deltaY: e.deltaY,
      deltaZ: e.deltaZ,
      deltaMode: e.deltaMode,
      x: e.clientX,
      y: e.clientY,
    });
  }

  // --- Focus ---
  _handleFocus(e) {
    if (!this.config.captureFocus) return;
    this._addEvent({
      type: 'focus',
      target: e.target ? e.target.tagName + (e.target.id ? '#' + e.target.id : '') : null,
    });
  }

  _handleBlur(e) {
    if (!this.config.captureFocus) return;
    this._addEvent({
      type: 'blur',
      target: e.target ? e.target.tagName + (e.target.id ? '#' + e.target.id : '') : null,
    });
  }

  _handleFocusIn(e) {
    if (!this.config.captureFocus) return;
    this._addEvent({
      type: 'focusin',
      target: e.target ? e.target.tagName + (e.target.id ? '#' + e.target.id : '') : null,
    });
  }

  _handleFocusOut(e) {
    if (!this.config.captureFocus) return;
    this._addEvent({
      type: 'focusout',
      target: e.target ? e.target.tagName + (e.target.id ? '#' + e.target.id : '') : null,
    });
  }

  // --- Clipboard ---
  _handleClipboard(action, e) {
    if (!this.config.captureClipboard) return;
    this._addEvent({
      type: 'clipboard',
      action: action,
      target: e.target ? e.target.tagName : null,
    });
  }

  // --- Resize ---
  _handleResize() {
    if (!this.config.captureResize) return;
    if (this._resizeThrottled) return;
    this._resizeThrottled = true;
    setTimeout(() => { this._resizeThrottled = false; }, 300);
    this._addEvent({
      type: 'resize',
      width: window.innerWidth,
      height: window.innerHeight,
      outerWidth: window.outerWidth,
      outerHeight: window.outerHeight,
    });
  }

  // --- Visibility ---
  _handleVisibilityChange() {
    if (!this.config.captureVisibility) return;
    this._addEvent({
      type: 'visibilitychange',
      state: document.visibilityState,
      hidden: document.hidden,
    });
    if (document.hidden) {
      this._frozen = true;
    } else {
      this._frozen = false;
    }
  }

  // --- Navigation ---
  _handlePopState(e) {
    if (!this.config.captureNavigation) return;
    this._addEvent({
      type: 'popstate',
      url: document.location.href,
    });
  }

  _handleBeforeUnload() {
    if (!this.config.captureNavigation) return;
    if (this.events.length > 0) {
      const payload = this.getPayload();
      try {
        const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
        navigator.sendBeacon(this.config.endpoint, blob);
      } catch (err) {
        this._warn('sendBeacon failed:', err);
      }
    }
  }

  // --- Batching ---
  _flush() {
    if (this.events.length === 0) return;
    const payload = this.getPayload();
    const events = this.events;
    this.events = [];
    this._sendBatch(payload, events);
  }

  async _sendBatch(payload, originalEvents) {
    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }
      this._retryCount = 0;
      this._log('Batch submitted:', payload.session_id, payload.events.length, 'events');
    } catch (err) {
      this._warn('Batch submission failed:', err.message);
      if (this._retryCount < this.config.maxRetries) {
        this._retryCount++;
        const delay = this.config.retryBaseDelay * Math.pow(2, this._retryCount - 1);
        this._log(`Retrying in ${delay}ms (attempt ${this._retryCount}/${this.config.maxRetries})`);
        setTimeout(() => {
          this._sendBatch(payload, originalEvents);
        }, delay);
      } else {
        this._warn('Max retries reached. Dropping batch.');
        this.events = originalEvents.concat(this.events);
      }
    }
  }

  _startBatchTimer() {
    this._stopBatchTimer();
    this._batchTimer = setInterval(() => {
      this._flush();
    }, this.config.batchInterval);
  }

  _stopBatchTimer() {
    if (this._batchTimer) {
      clearInterval(this._batchTimer);
      this._batchTimer = null;
    }
  }

  _checkSessionTimeout() {
    const elapsed = this._timestamp() - this._lastActivity;
    if (elapsed > this.config.sessionTimeout) {
      this._log('Session timed out after inactivity');
      this.stop();
      this.sessionId = this._generateId('sess_');
      this._frozen = false;
      this.start();
    }
  }

  _startSessionMonitor() {
    this._sessionMonitor = setInterval(() => {
      this._checkSessionTimeout();
    }, Math.min(this.config.sessionTimeout / 4, 60000));
  }

  _stopSesionMonitor() {
    if (this._sessionMonitor) {
      clearInterval(this._sessionMonitor);
      this._sessionMonitor = null;
    }
  }

  // --- Fingerprinting ---
  async getFingerprint() {
    if (this._fingerprint) return this._fingerprint;
    const components = {};

    components.userAgent = navigator.userAgent;
    components.platform = navigator.platform;
    components.language = navigator.language;
    components.languages = navigator.languages;
    components.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    components.timezoneOffset = new Date().getTimezoneOffset();

    components.screenWidth = screen.width;
    components.screenHeight = screen.height;
    components.screenAvailWidth = screen.availWidth;
    components.screenAvailHeight = screen.availHeight;
    components.colorDepth = screen.colorDepth;
    components.pixelDepth = screen.pixelDepth;
    components.devicePixelRatio = window.devicePixelRatio || 1;

    try {
      components.hardwareConcurrency = navigator.hardwareConcurrency;
      components.deviceMemory = navigator.deviceMemory;
      components.maxTouchPoints = navigator.maxTouchPoints;
    } catch (_) {}

    try {
      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 256;
      const ctx = canvas.getContext('2d');
      ctx.textBaseline = 'alphabetic';
      ctx.fillStyle = '#f60';
      ctx.fillRect(100, 1, 62, 20);
      ctx.fillStyle = '#069';
      ctx.font = '14px Arial';
      ctx.fillText('BehaviorTracker', 5, 40);
      ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
      ctx.font = '18px Courier New';
      ctx.fillText('fp', 12, 75);
      ctx.fillStyle = '#333';
      ctx.font = '16px Georgia';
      ctx.fillText('biometric', 20, 110);
      ctx.beginPath();
      ctx.arc(128, 180, 40, 0, Math.PI * 2, true);
      ctx.strokeStyle = '#123';
      ctx.lineWidth = 3;
      ctx.stroke();
      components.canvasFingerprint = canvas.toDataURL();
    } catch (_) {}

    try {
      const gl = document.createElement('canvas').getContext('webgl');
      if (gl) {
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) {
          components.webglVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
          components.webglRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        }
        components.webglVersion = gl.getParameter(gl.VERSION);
        components.webglShadingLanguage = gl.getParameter(gl.SHADING_LANGUAGE_VERSION);
      }
    } catch (_) {}

    try {
      const actx = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = actx.createAnalyser();
      const oscillator = actx.createOscillator();
      oscillator.type = 'sawtooth';
      oscillator.frequency.setValueAtTime(1000, actx.currentTime);
      oscillator.connect(analyser);
      oscillator.start();
      const buffer = new Float32Array(analyser.frequencyBinCount);
      analyser.getFloatFrequencyData(buffer);
      const sum = buffer.reduce((a, b) => a + Math.abs(b), 0);
      components.audioFingerprint = sum;
      actx.close();
    } catch (_) {}

    try {
      const fonts = [
        'Arial', 'Arial Black', 'Arial Narrow', 'Calibri', 'Cambria',
        'Cambria Math', 'Comic Sans MS', 'Courier', 'Courier New',
        'Georgia', 'Helvetica', 'Impact', 'Lucida Console',
        'Lucida Sans Unicode', 'Microsoft Sans Serif', 'Palatino Linotype',
        'Segoe UI', 'Segoe UI Light', 'Segoe UI Semibold', 'Segoe UI Symbol',
        'Tahoma', 'Times New Roman', 'Trebuchet MS', 'Verdana',
      ];
      const detected = [];
      const testDiv = document.createElement('div');
      testDiv.innerHTML = 'abcdefghijklmnopqrstuvwxyz0123456789';
      testDiv.style.position = 'absolute';
      testDiv.style.left = '-9999px';
      testDiv.style.visibility = 'hidden';
      document.body.appendChild(testDiv);
      const baseWidth = testDiv.offsetWidth;
      for (const font of fonts) {
        testDiv.style.fontFamily = `"${font}", monospace`;
        if (testDiv.offsetWidth !== baseWidth) {
          detected.push(font);
        }
      }
      document.body.removeChild(testDiv);
      components.installedFonts = detected;
    } catch (_) {}

    const hashInput = JSON.stringify(components);
    const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(hashInput));
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    components.combinedHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    this._fingerprint = components;
    return components;
  }

  // --- Public API ---
  start() {
    if (this._isTracking) return;
    this._isTracking = true;
    this._log('Starting tracking, session:', this.sessionId);

    if (this.config.captureKeys) {
      this._addListener(document, 'keydown', this._bound.handleKeyDown);
      this._addListener(document, 'keyup', this._bound.handleKeyUp);
    }
    if (this.config.captureMouse) {
      this._addListener(document, 'mousemove', this._bound.handleMouseMove);
      this._addListener(document, 'mousedown', this._bound.handleMouseDown);
      this._addListener(document, 'mouseup', this._bound.handleMouseUp);
      this._addListener(document, 'click', this._bound.handleClick);
      this._addListener(document, 'contextmenu', this._bound.handleContextMenu);
      this._addListener(document, 'dblclick', this._bound.handleDblClick);
    }
    if (this.config.captureTouch) {
      this._addListener(document, 'touchstart', this._bound.handleTouchStart, { passive: true });
      this._addListener(document, 'touchmove', this._bound.handleTouchMove, { passive: true });
      this._addListener(document, 'touchend', this._bound.handleTouchEnd, { passive: true });
    }
    if (this.config.captureScroll) {
      this._addListener(window, 'scroll', this._bound.handleScroll, { passive: true });
      this._addListener(document, 'wheel', this._bound.handleWheel, { passive: true });
    }
    if (this.config.captureFocus) {
      this._addListener(window, 'focus', this._bound.handleFocus);
      this._addListener(window, 'blur', this._bound.handleBlur);
      this._addListener(document, 'focusin', this._bound.handleFocusIn);
      this._addListener(document, 'focusout', this._bound.handleFocusOut);
    }
    if (this.config.captureClipboard) {
      this._addListener(document, 'copy', this._bound.handleCopy);
      this._addListener(document, 'cut', this._bound.handleCut);
      this._addListener(document, 'paste', this._bound.handlePaste);
    }
    if (this.config.captureResize) {
      this._addListener(window, 'resize', this._bound.handleResize);
    }
    if (this.config.captureVisibility) {
      this._addListener(document, 'visibilitychange', this._bound.handleVisibilityChange);
    }
    if (this.config.captureNavigation) {
      this._addListener(window, 'popstate', this._bound.handlePopState);
      this._addListener(window, 'beforeunload', this._bound.handleBeforeUnload);
    }
    if (this.config.fingerprint) {
      this.getFingerprint().then(fp => {
        this._log('Fingerprint:', fp.combinedHash);
      });
    }

    this._startBatchTimer();
    this._startSessionMonitor();
  }

  stop() {
    if (!this._isTracking) return;
    this._flush();
    this._removeListeners();
    this._stopBatchTimer();
    this._stopSesionMonitor();
    this._isTracking = false;
    this._log('Stopped tracking');
  }

  getPayload() {
    const fpStr = this._fingerprint 
      ? (typeof this._fingerprint === 'string' ? this._fingerprint : this._fingerprint.combinedHash || JSON.stringify(this._fingerprint))
      : null;
    const payload = {
      session_id: this.sessionId,
      user_id: this.userId,
      device_type: 'web',
      device_fingerprint: fpStr,
      events: this.events,
      fingerprint: this._fingerprint,
      event_count: this.events.length,
      duration: this.events.length > 0
        ? this.events[this.events.length - 1].ts - this.events[0].ts
        : 0,
    };
    return payload;
  }

  async submit(endpoint) {
    const url = endpoint || this.config.endpoint;
    if (this.events.length === 0) {
      throw new Error('No behavioral events recorded');
    }
    const payload = this.getPayload();
    if (this._fingerprint) {
      payload.fingerprint = this._fingerprint;
    }
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Submission failed: ${await response.text()}`);
    }
    this.events = [];
    return response.json();
  }

  getSessionId() {
    return this.sessionId;
  }

  clearEvents() {
    this.events = [];
  }

  getEventCount() {
    return this.events.length;
  }

  onEvent(callback) {
    if (typeof callback === 'function') {
      this._onEventCallbacks.push(callback);
    }
  }

  offEvent(callback) {
    const idx = this._onEventCallbacks.indexOf(callback);
    if (idx !== -1) {
      this._onEventCallbacks.splice(idx, 1);
    }
  }

  destroy() {
    this.stop();
    this._onEventCallbacks = [];
    this.events = [];
    this._fingerprint = null;
    this._lastMousePos = null;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = BehavioralTracker;
}
