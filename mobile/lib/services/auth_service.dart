import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class AuthService {
  static Future<Map<String, dynamic>> register({
    required String fullName,
    required String email,
    required String phone,
    required String password,
    required String role,
  }) async {
    final res = await ApiService.post('/auth/register', {
      'full_name': fullName,
      'email': email,
      'phone': phone,
      'password': password,
      'role': role,
    });
    if (res.statusCode == 201) {
      final data = jsonDecode(res.body);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', data['access_token']);
      await prefs.setString('user', jsonEncode(data['user']));
      return {'success': true, 'user': data['user']};
    }
    final err = jsonDecode(res.body);
    return {'success': false, 'message': err['detail'] ?? 'Registration failed'};
  }

  static Future<Map<String, dynamic>> login(String email, String password) async {
    final res = await ApiService.post('/auth/login', {
      'email': email,
      'password': password,
    });
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', data['access_token']);
      await prefs.setString('user', jsonEncode(data['user']));
      return {'success': true, 'user': data['user']};
    }
    if (res.statusCode == 401 || res.statusCode == 400) {
      return {'success': false, 'message': 'Invalid email or password'};
    }
    if (res.statusCode == 422) {
      return {'success': false, 'message': 'Please enter a valid email and password'};
    }
    try {
      final err = jsonDecode(res.body);
      return {'success': false, 'message': err['detail'] ?? 'Login failed'};
    } catch (_) {
      return {'success': false, 'message': 'Login failed. Please try again'};
    }
  }

  static Future<Map<String, dynamic>?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userStr = prefs.getString('user');
    if (userStr == null) return null;
    return jsonDecode(userStr);
  }

  static Future<bool> isLoggedIn() async {
    final token = await ApiService.getToken();
    return token != null;
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('user');
  }
}
