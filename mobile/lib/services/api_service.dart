import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final Map<String, dynamic>? errors;

  ApiException(this.message, {this.statusCode, this.errors});

  @override
  String toString() => message;
}

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  final http.Client _client = http.Client();

  String? _accessToken;
  String? _refreshToken;

  Future<void> init() async {
    _accessToken = await _storage.read(key: 'access_token');
    _refreshToken = await _storage.read(key: 'refresh_token');
  }

  Future<Map<String, String>> _getHeaders({
    bool auth = true,
    bool jsonContent = true,
  }) async {
    final headers = <String, String>{
      'Accept': 'application/json',
    };

    if (jsonContent) {
      headers['Content-Type'] = 'application/json';
    }

    if (auth && _accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }

    return headers;
  }

  Future<dynamic> _handleResponse(http.Response response) async {
    final body = response.body.isNotEmpty ? jsonDecode(response.body) : null;

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body;
    }

    if (response.statusCode == 401) {
      final refreshed = await _tryRefreshToken();
      if (refreshed) {
        throw ApiException('Token refreshed, retry request',
            statusCode: 401);
      }
      await _clearTokens();
      throw ApiException('Session expired. Please login again.',
          statusCode: 401);
    }

    String message = 'Request failed';
    if (body != null) {
      message = body['message'] ??
          body['detail'] ??
          body['error'] ??
          'Request failed';
    }

    throw ApiException(
      message,
      statusCode: response.statusCode,
      errors: body is Map<String, dynamic>
          ? body['errors'] as Map<String, dynamic>?
          : null,
    );
  }

  Future<dynamic> get(String endpoint,
      {Map<String, String>? queryParams, bool auth = true}) async {
    try {
      var uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      if (queryParams != null && queryParams.isNotEmpty) {
        uri = uri.replace(queryParameters: queryParams);
      }

      final response = await _client
          .get(uri, headers: await _getHeaders(auth: auth))
          .timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } on SocketException {
      throw ApiException('No internet connection');
    } on http.ClientException {
      throw ApiException('Connection error');
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException('An unexpected error occurred');
    }
  }

  Future<dynamic> post(String endpoint,
      {Map<String, dynamic>? body, bool auth = true}) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      final response = await _client
          .post(
            uri,
            headers: await _getHeaders(auth: auth),
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } on SocketException {
      throw ApiException('No internet connection');
    } on http.ClientException {
      throw ApiException('Connection error');
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException('An unexpected error occurred');
    }
  }

  Future<dynamic> put(String endpoint,
      {Map<String, dynamic>? body, bool auth = true}) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      final response = await _client
          .put(
            uri,
            headers: await _getHeaders(auth: auth),
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } on SocketException {
      throw ApiException('No internet connection');
    } on http.ClientException {
      throw ApiException('Connection error');
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException('An unexpected error occurred');
    }
  }

  Future<dynamic> delete(String endpoint, {bool auth = true}) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}$endpoint');
      final response = await _client
          .delete(uri, headers: await _getHeaders(auth: auth))
          .timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } on SocketException {
      throw ApiException('No internet connection');
    } on http.ClientException {
      throw ApiException('Connection error');
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException('An unexpected error occurred');
    }
  }

  Future<bool> _tryRefreshToken() async {
    if (_refreshToken == null) return false;

    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}${ApiConfig.refreshToken}');
      final response = await _client
          .post(
            uri,
            headers: await _getHeaders(auth: false),
            body: jsonEncode({'refresh_token': _refreshToken}),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await setTokens(
          data['access_token'] ?? data['accessToken'],
          data['refresh_token'] ?? data['refreshToken'],
        );
        return true;
      }
    } catch (_) {}

    return false;
  }

  Future<void> setTokens(String? accessToken, String? refreshToken) async {
    _accessToken = accessToken;
    _refreshToken = refreshToken;

    if (accessToken != null) {
      await _storage.write(key: 'access_token', value: accessToken);
    } else {
      await _storage.delete(key: 'access_token');
    }

    if (refreshToken != null) {
      await _storage.write(key: 'refresh_token', value: refreshToken);
    } else {
      await _storage.delete(key: 'refresh_token');
    }
  }

  Future<void> _clearTokens() async {
    _accessToken = null;
    _refreshToken = null;
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  Future<void> clearSession() async {
    await _clearTokens();
  }

  bool get isAuthenticated => _accessToken != null;

  String? get accessToken => _accessToken;
}
