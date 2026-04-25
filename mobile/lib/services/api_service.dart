import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // 10.0.2.2 = Android emulator, localhost = Chrome/web
  // For real Android device: use your PC's WiFi IP (run `ipconfig` to find it)
  static const String baseUrl = 'https://zoogloeal-nonprescribed-lovella.ngrok-free.dev';

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }

  static Future<Map<String, String>> authHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  static const Duration _timeout = Duration(seconds: 30);

  static Future<http.Response> get(String path) async {
    final headers = await authHeaders();
    return http.get(Uri.parse('$baseUrl$path'), headers: headers).timeout(_timeout);
  }

  static Future<http.Response> post(String path, Map<String, dynamic> body) async {
    final headers = await authHeaders();
    return http.post(
      Uri.parse('$baseUrl$path'),
      headers: headers,
      body: jsonEncode(body),
    ).timeout(_timeout);
  }

  static Future<http.Response> put(String path, Map<String, dynamic> body) async {
    final headers = await authHeaders();
    return http.put(
      Uri.parse('$baseUrl$path'),
      headers: headers,
      body: jsonEncode(body),
    ).timeout(_timeout);
  }

  static Future<http.Response> patch(String path, Map<String, dynamic> body) async {
    final headers = await authHeaders();
    return http.patch(
      Uri.parse('$baseUrl$path'),
      headers: headers,
      body: jsonEncode(body),
    ).timeout(_timeout);
  }
}
