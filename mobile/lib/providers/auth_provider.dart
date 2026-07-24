import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';
import '../services/biometric_service.dart';
import '../services/behavioral_service.dart';

enum AuthStatus { uninitialized, authenticated, unauthenticated, loading }

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  final BiometricService _biometricService = BiometricService();
  final BehavioralService _behavioralService = BehavioralService();

  AuthStatus _status = AuthStatus.uninitialized;
  UserModel? _user;
  String? _error;
  bool _isLoading = false;
  bool _biometricAvailable = false;
  String _biometricType = 'Biometric';

  AuthStatus get status => _status;
  UserModel? get user => _user;
  String? get error => _error;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _status == AuthStatus.authenticated;
  bool get biometricAvailable => _biometricAvailable;
  String get biometricType => _biometricType;

  Future<void> init() async {
    _status = AuthStatus.loading;
    notifyListeners();

    try {
      await _authService.init();
      await _biometricService.init();

      _biometricAvailable = await _biometricService.isBiometricAvailable();
      if (_biometricAvailable) {
        _biometricType = await _biometricService.getBiometricTypeName();
      }

      if (_authService.isAuthenticated) {
        try {
          _user = await _authService.getProfile();
          _status = AuthStatus.authenticated;
          _behavioralService.startCollection();
        } catch (_) {
          _status = AuthStatus.unauthenticated;
        }
      } else {
        _status = AuthStatus.unauthenticated;
      }
    } catch (_) {
      _status = AuthStatus.unauthenticated;
    }

    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _authService.login(email, password);
      _user = UserModel.fromJson(response['user'] ?? response);
      _status = AuthStatus.authenticated;
      _behavioralService.startCollection();

      if (_biometricAvailable) {
        await _biometricService.enableBiometricLogin();
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> loginWithBiometrics() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final authenticated = await _biometricService.loginWithBiometrics();
      if (!authenticated) {
        _error = 'Biometric authentication failed';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      if (_authService.isAuthenticated) {
        _user = await _authService.getProfile();
        _status = AuthStatus.authenticated;
        _behavioralService.startCollection();
        _isLoading = false;
        notifyListeners();
        return true;
      }

      _error = 'Please login with your credentials first';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(Map<String, dynamic> userData) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _authService.register(userData);
      if (response['access_token'] != null || response['accessToken'] != null) {
        await _authService.init();
        _user = UserModel.fromJson(response['user'] ?? response);
        _status = AuthStatus.authenticated;
        _behavioralService.startCollection();
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyOtp(String email, String otp, String purpose) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _authService.verifyOtp(email, otp, purpose);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> forgotPassword(String email) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _authService.forgotPassword(email);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> resetPassword(
      String email, String otp, String newPassword) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _authService.resetPassword(email, otp, newPassword);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> setupMfa(String method) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _authService.setupMfa(method);
      _user = _user?.copyWith(isMfaEnabled: true);
      _isLoading = false;
      notifyListeners();
      return response.isNotEmpty;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyMfa(String code) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final verified = await _authService.verifyMfa(code);
      _isLoading = false;
      notifyListeners();
      return verified;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateProfile(Map<String, dynamic> data) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _user = await _authService.updateProfile(data);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    _behavioralService.stopCollection();
    await _authService.logout();
    _user = null;
    _status = AuthStatus.unauthenticated;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
