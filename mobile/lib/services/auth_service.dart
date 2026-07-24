import '../config/api_config.dart';
import '../models/user_model.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _api = ApiService();

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _api.post(ApiConfig.login, body: {
      'email': email,
      'password': password,
    }, auth: false);

    if (response != null) {
      await _api.setTokens(
        response['access_token'] ?? response['accessToken'],
        response['refresh_token'] ?? response['refreshToken'],
      );
    }

    return response ?? {};
  }

  Future<Map<String, dynamic>> register(Map<String, dynamic> userData) async {
    final response = await _api.post(ApiConfig.register, body: userData, auth: false);
    return response ?? {};
  }

  Future<Map<String, dynamic>> verifyOtp(String email, String otp, String purpose) async {
    final response = await _api.post(ApiConfig.verifyOtp, body: {
      'email': email,
      'otp': otp,
      'purpose': purpose,
    }, auth: false);
    return response ?? {};
  }

  Future<Map<String, dynamic>> forgotPassword(String email) async {
    final response = await _api.post(ApiConfig.forgotPassword, body: {
      'email': email,
    }, auth: false);
    return response ?? {};
  }

  Future<Map<String, dynamic>> resetPassword(
      String email, String otp, String newPassword) async {
    final response = await _api.post(ApiConfig.resetPassword, body: {
      'email': email,
      'otp': otp,
      'new_password': newPassword,
    }, auth: false);
    return response ?? {};
  }

  Future<Map<String, dynamic>> setupMfa(String method) async {
    final response = await _api.post(ApiConfig.mfaSetup, body: {
      'method': method,
    });
    return response ?? {};
  }

  Future<bool> verifyMfa(String code) async {
    final response = await _api.post(ApiConfig.mfaVerify, body: {
      'code': code,
    });
    return response?['verified'] == true;
  }

  Future<UserModel> getProfile() async {
    final response = await _api.get(ApiConfig.profile);
    return UserModel.fromJson(response ?? {});
  }

  Future<UserModel> updateProfile(Map<String, dynamic> data) async {
    final response = await _api.put(ApiConfig.updateProfile, body: data);
    return UserModel.fromJson(response ?? {});
  }

  Future<void> logout() async {
    await _api.clearSession();
  }

  Future<bool> checkEmailExists(String email) async {
    try {
      await _api.get('/auth/check-email', queryParams: {'email': email}, auth: false);
      return true;
    } catch (_) {
      return false;
    }
  }
}
