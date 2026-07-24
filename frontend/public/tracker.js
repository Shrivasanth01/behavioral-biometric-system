(function () {
  'use strict';

  var BehavioralTracker = function (options) {
    this.options = Object.assign({
      userId: null,
      sessionId: null,
      endpoint: '/api/behavioral/events',
      sampleRate: 50,
      batchSize: 100,
      uploadInterval: 30000,
      enabled: true,
    }, options);

    this.events = [];
    this.sessionData = {};
    this.isTracking = false;
    this.listeners = [];
    this._init();
  };

  BehavioralTracker.prototype._init = function () {
    if (!this.options.enabled) return;
    this.sessionData = this._captureDeviceInfo();
    this._startTracking();
    this._startUploadInterval();
    this._sendSessionStart();
  };

  BehavioralTracker.prototype._captureDeviceInfo = function () {
    var info = {
      screenResolution: screen.width + 'x' + screen.height,
      colorDepth: screen.colorDepth,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      platform: navigator.platform,
      userAgent: navigator.userAgent,
      hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
      deviceMemory: navigator.deviceMemory || 'unknown',
      touchSupport: 'ontouchstart' in window,
      maxTouchPoints: navigator.maxTouchPoints || 0,
    };

    try {
      var canvas = document.createElement('canvas');
      canvas.width = 200;
      canvas.height = 50;
      var ctx = canvas.getContext('2d');
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillStyle = '#f60';
      ctx.fillRect(125, 1, 62, 20);
      ctx.fillStyle = '#069';
      ctx.fillText('BehavioralBio', 2, 15);
      ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
      ctx.fillText('Crypto', 4, 17);
      info.canvasFingerprint = canvas.toDataURL();
    } catch (e) {
      info.canvasFingerprint = 'unsupported';
    }

    try {
      var gl = document.createElement('canvas').getContext('webgl');
      if (gl) {
        var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) {
          info.webglVendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
          info.webglRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        }
      }
    } catch (e) {
      info.webglVendor = 'unsupported';
    }

    try {
      var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      var oscillator = audioCtx.createOscillator();
      var analyser = audioCtx.createAnalyser();
      oscillator.connect(analyser);
      oscillator.frequency.value = 440;
      info.audioSupported = true;
      audioCtx.close();
    } catch (e) {
      info.audioSupported = false;
    }

    return info;
  };

  BehavioralTracker.prototype._startTracking = function () {
    if (this.isTracking) return;
    this.isTracking = true;

    var self = this;
    var lastMouseMove = 0;
    var lastKeyEvent = 0;

    var keyHandler = function (event) {
      var now = Date.now();
      if (now - lastKeyEvent < self.options.sampleRate) return;
      lastKeyEvent = now;

      self._addEvent('keyboard', {
        key: event.key,
        code: event.code,
        type: event.type,
        altKey: event.altKey,
        ctrlKey: event.ctrlKey,
        shiftKey: event.shiftKey,
        metaKey: event.metaKey,
        repeat: event.repeat,
        location: event.location,
      });
    };

    var mouseMoveHandler = function (event) {
      var now = Date.now();
      if (now - lastMouseMove < self.options.sampleRate) return;
      lastMouseMove = now;

      self._addEvent('mousemove', {
        x: event.clientX,
        y: event.clientY,
        movementX: event.movementX || 0,
        movementY: event.movementY || 0,
      });
    };

    var mouseClickHandler = function (event) {
      self._addEvent('click', {
        x: event.clientX,
        y: event.clientY,
        button: event.button,
        buttons: event.buttons,
        target: event.target ? event.target.tagName : 'unknown',
        targetClass: event.target ? event.target.className : '',
      });
    };

    var scrollHandler = function () {
      self._addEvent('scroll', {
        scrollX: window.scrollX,
        scrollY: window.scrollY,
        scrollXMax: document.documentElement.scrollWidth - window.innerWidth,
        scrollYMax: document.documentElement.scrollHeight - window.innerHeight,
      });
    };

    var focusHandler = function () {
      self._addEvent('focus', {});
    };

    var blurHandler = function () {
      self._addEvent('blur', {});
    };

    var visibilityHandler = function () {
      self._addEvent('visibility', {
        state: document.visibilityState,
      });
    };

    var resizeHandler = function () {
      self._addEvent('resize', {
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    document.addEventListener('keydown', keyHandler);
    document.addEventListener('keyup', keyHandler);
    document.addEventListener('mousemove', mouseMoveHandler);
    document.addEventListener('click', mouseClickHandler);
    document.addEventListener('scroll', scrollHandler);
    window.addEventListener('focus', focusHandler);
    window.addEventListener('blur', blurHandler);
    document.addEventListener('visibilitychange', visibilityHandler);
    window.addEventListener('resize', resizeHandler);

    this.listeners = [
      { el: document, event: 'keydown', handler: keyHandler },
      { el: document, event: 'keyup', handler: keyHandler },
      { el: document, event: 'mousemove', handler: mouseMoveHandler },
      { el: document, event: 'click', handler: mouseClickHandler },
      { el: document, event: 'scroll', handler: scrollHandler },
      { el: window, event: 'focus', handler: focusHandler },
      { el: window, event: 'blur', handler: blurHandler },
      { el: document, event: 'visibilitychange', handler: visibilityHandler },
      { el: window, event: 'resize', handler: resizeHandler },
    ];
  };

  BehavioralTracker.prototype._stopTracking = function () {
    this.isTracking = false;
    this.listeners.forEach(function (item) {
      item.el.removeEventListener(item.event, item.handler);
    });
    this.listeners = [];
  };

  BehavioralTracker.prototype._addEvent = function (type, data) {
    this.events.push({
      type: type,
      timestamp: Date.now(),
      data: data,
      sessionId: this.options.sessionId,
      userId: this.options.userId,
    });

    if (this.events.length >= this.options.batchSize) {
      this._uploadEvents();
    }
  };

  BehavioralTracker.prototype._uploadEvents = function () {
    if (this.events.length === 0) return;

    var events = this.events.splice(0, this.options.batchSize);

    try {
      var payload = JSON.stringify({ events: events });

      if (navigator.sendBeacon) {
        navigator.sendBeacon(this.options.endpoint, new Blob([payload], { type: 'application/json' }));
      } else {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', this.options.endpoint, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(payload);
      }
    } catch (e) {
      this.events = events.concat(this.events);
    }
  };

  BehavioralTracker.prototype._startUploadInterval = function () {
    var self = this;
    this._uploadTimer = setInterval(function () {
      self._uploadEvents();
    }, this.options.uploadInterval);
  };

  BehavioralTracker.prototype._sendSessionStart = function () {
    this._addEvent('session_start', {
      deviceInfo: this.sessionData,
      referrer: document.referrer,
      pageUrl: window.location.href,
      pageTitle: document.title,
    });
  };

  BehavioralTracker.prototype.sendEvent = function (type, data) {
    this._addEvent(type, data);
  };

  BehavioralTracker.prototype.flush = function () {
    this._uploadEvents();
  };

  BehavioralTracker.prototype.destroy = function () {
    this.flush();
    this._stopTracking();
    if (this._uploadTimer) {
      clearInterval(this._uploadTimer);
    }
    this.events = [];
  };

  BehavioralTracker.prototype.getSessionData = function () {
    return this.sessionData;
  };

  BehavioralTracker.createLoginCapture = function () {
    var events = [];
    var capturing = false;
    var handler = function (event) {
      if (!capturing) return;
      events.push({
        type: event.type,
        key: event.key,
        code: event.code,
        timestamp: Date.now(),
        timeSinceLastEvent: events.length > 0 ? Date.now() - events[events.length - 1].timestamp : 0,
      });
    };

    return {
      start: function () {
        events = [];
        capturing = true;
        document.addEventListener('keydown', handler);
        document.addEventListener('keyup', handler);
        document.addEventListener('mousemove', handler);
      },
      stop: function () {
        capturing = false;
        document.removeEventListener('keydown', handler);
        document.removeEventListener('keyup', handler);
        document.removeEventListener('mousemove', handler);
        var capturedEvents = events.slice();
        events = [];
        return capturedEvents;
      },
      getEvents: function () {
        return events.slice();
      },
    };
  };

  window.BehavioralTracker = BehavioralTracker;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      window.dispatchEvent(new CustomEvent('behavioralTrackerReady'));
    });
  } else {
    setTimeout(function () {
      window.dispatchEvent(new CustomEvent('behavioralTrackerReady'));
    }, 0);
  }
})();
