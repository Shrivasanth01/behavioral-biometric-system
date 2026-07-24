import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:local_auth/local_auth.dart';
import 'package:biometric_storage/biometric_storage.dart';

class BiometricService {
  final LocalAuthentication _localAuth = LocalAuthentication();
  BiometricStorage? _storage;

  Future<void> init() async {
    try {
      _storage = await BiometricStorage().canAccess('banking_credential');
    } catch (_) {
      _storage = null;
    }
  }

  Future<bool> isBiometricAvailable() async {
    try {
      return await _localAuth.canCheckBiometrics;
    } catch (e) {
      return false;
    }
  }

  Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      return await _localAuth.getAvailableBiometrics();
    } catch (e) {
      return [];
    }
  }

  Future<bool> authenticate({
    String reason = 'Authenticate to access your banking account',
    bool stickyAuth = true,
  }) async {
    try {
      return await _localAuth.authenticate(
        localizedReason: reason,
        options: AuthenticationOptions(
          stickyAuth: stickyAuth,
          biometricOnly: false,
        ),
      );
    } on PlatformException catch (e) {
      if (kDebugMode) {
        debugPrint('Biometric auth error: ${e.message}');
      }
      return false;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('Biometric auth error: $e');
      }
      return false;
    }
  }

  Future<bool> saveCredential(String key, String value) async {
    try {
      final storage = _storage;
      if (storage == null) return false;

      final canAccess = await storage.canAccess(key);
      if (canAccess) {
        final file = await BiometricStorage().getStorage(key);
        await file.write(value);
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  Future<String?> readCredential(String key) async {
    try {
      final storage = _storage;
      if (storage == null) return null;

      final canAccess = await storage.canAccess(key);
      if (canAccess) {
        final file = await BiometricStorage().getStorage(key);
        return await file.read();
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  Future<bool> deleteCredential(String key) async {
    try {
      final storage = _storage;
      if (storage == null) return false;

      final file = await BiometricStorage().getStorage(key);
      await file.delete();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> enableBiometricLogin() async {
    final available = await isBiometricAvailable();
    if (!available) return false;

    final authenticated = await authenticate(
      reason: 'Enable biometric login for faster access',
    );
    if (!authenticated) return false;

    return await saveCredential(
      'biometric_login',
      'enabled',
    );
  }

  Future<bool> isBiometricLoginEnabled() async {
    final value = await readCredential('biometric_login');
    return value == 'enabled';
  }

  Future<bool> loginWithBiometrics() async {
    final enabled = await isBiometricLoginEnabled();
    if (!enabled) return false;

    return await authenticate(
      reason: 'Login to your banking account',
    );
  }

  Future<void> disableBiometricLogin() async {
    await deleteCredential('biometric_login');
  }

  String get biometricTypeName {
    return 'Biometric';
  }

  Future<String> getBiometricTypeName() async {
    try {
      final types = await getAvailableBiometrics();
      if (types.contains(BiometricType.face)) return 'Face ID';
      if (types.contains(BiometricType.fingerprint)) return 'Fingerprint';
      if (types.contains(BiometricType.iris)) return 'Iris';
      return 'Biometric';
    } catch (_) {
      return 'Biometric';
    }
  }
}
