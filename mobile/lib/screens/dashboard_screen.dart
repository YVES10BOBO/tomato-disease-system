import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

String _formatDate(DateTime d) {
  const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return '${days[d.weekday - 1]}, ${d.day} ${months[d.month - 1]} ${d.year}';
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _summary;
  Map<String, dynamic>? _sensor;
  Map<String, dynamic>? _user;
  String? _farmId;
  bool _loading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() { _loading = true; _error = ''; });
    try {
      _user = await AuthService.getUser();
      // Get farm
      final farmRes = await ApiService.get('/farms/');
      if (farmRes.statusCode == 200) {
        final farms = jsonDecode(farmRes.body)['farms'];
        if (farms != null && farms.isNotEmpty) {
          _farmId = farms[0]['id'];
        }
      }
      if (_farmId == null) {
        setState(() { _loading = false; });
        return;
      }
      // Load data in parallel
      final results = await Future.wait([
        ApiService.get('/alerts/farm/$_farmId/summary'),
        ApiService.get('/iot/sensors/$_farmId/latest'),
      ]);
      setState(() {
        if (results[0].statusCode == 200) _summary = jsonDecode(results[0].body);
        if (results[1].statusCode == 200) _sensor = jsonDecode(results[1].body);
        _loading = false;
      });
    } catch (e) {
      setState(() { _error = 'Failed to load data'; _loading = false; });
    }
  }

  Color _healthColor(String? health) {
    switch (health) {
      case 'CRITICAL': return Colors.red;
      case 'HIGH RISK': return Colors.orange;
      case 'MODERATE RISK': return Colors.amber;
      default: return const Color(0xFF2E7D32);
    }
  }

  Color _riskColor(String? risk) {
    switch (risk?.toLowerCase()) {
      case 'critical': return Colors.red;
      case 'high': return Colors.orange;
      case 'medium': return Colors.amber;
      default: return const Color(0xFF2E7D32);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: const Row(
          children: [
            Text('🍅', style: TextStyle(fontSize: 22)),
            SizedBox(width: 8),
            Text('TomatoGuard', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32)))
          : _error.isNotEmpty
              ? Center(child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 48, color: Colors.red),
                    const SizedBox(height: 12),
                    Text(_error, style: const TextStyle(color: Colors.grey)),
                    const SizedBox(height: 16),
                    ElevatedButton(onPressed: _loadData, child: const Text('Retry')),
                  ],
                ))
              : RefreshIndicator(
                  onRefresh: _loadData,
                  color: const Color(0xFF2E7D32),
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Greeting
                        Text(
                          'Hello, ${_user?['full_name']?.split(' ').first ?? 'Farmer'} 👋',
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF1a1a1a)),
                        ),
                        Text(
                          _formatDate(DateTime.now()),
                          style: const TextStyle(color: Colors.grey, fontSize: 13),
                        ),
                        const SizedBox(height: 16),

                        // Health Banner
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: _healthColor(_summary?['overall_health']),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('Overall Farm Health',
                                      style: TextStyle(color: Colors.white70, fontSize: 12)),
                                    const SizedBox(height: 4),
                                    Text(
                                      _summary?['overall_health'] ?? 'HEALTHY',
                                      style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                                    ),
                                  ],
                                ),
                              ),
                              Text(
                                _summary?['overall_health'] == 'HEALTHY' ? '✅' :
                                _summary?['overall_health'] == 'CRITICAL' ? '🚨' : '⚠️',
                                style: const TextStyle(fontSize: 40),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Stats Row
                        Row(
                          children: [
                            _statCard('Active Diseases', '${_summary?['active_diseases'] ?? 0}',
                              Icons.coronavirus_outlined, Colors.red),
                            const SizedBox(width: 10),
                            _statCard('Alerts Today', '${_summary?['alerts_today'] ?? 0}',
                              Icons.notifications_outlined, Colors.orange),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            _statCard('Detections', '${_summary?['detections_today'] ?? 0}',
                              Icons.biotech_outlined, Colors.purple),
                            const SizedBox(width: 10),
                            _statCard('Zones Scanned', '${_summary?['scans_today'] ?? 0}',
                              Icons.camera_outlined, Colors.blue),
                          ],
                        ),
                        const SizedBox(height: 16),

                        // Live Sensor Card
                        if (_sensor != null) ...[
                          const Text('Live Sensor Readings',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 10),
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 10)],
                            ),
                            child: Column(
                              children: [
                                _sensorRow('🌡️', 'Temperature', '${_sensor!['temperature']}°C',
                                  _sensor!['temperature'] > 30 ? Colors.orange : const Color(0xFF2E7D32)),
                                const Divider(height: 20),
                                _sensorRow('💧', 'Humidity', '${_sensor!['humidity']}%',
                                  _sensor!['humidity'] > 85 ? Colors.blue.shade700 : const Color(0xFF2E7D32)),
                                const Divider(height: 20),
                                _sensorRow('🌱', 'Soil Moisture', '${_sensor!['soil_moisture']}%',
                                  (_sensor!['soil_moisture'] < 30 || _sensor!['soil_moisture'] > 80)
                                    ? Colors.orange : const Color(0xFF2E7D32)),
                                const SizedBox(height: 12),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: _riskColor(_sensor!['risk_level']).withAlpha(25),
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(color: _riskColor(_sensor!['risk_level']).withAlpha(76)),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Container(width: 8, height: 8,
                                        decoration: BoxDecoration(
                                          color: _riskColor(_sensor!['risk_level']),
                                          shape: BoxShape.circle,
                                        ),
                                      ),
                                      const SizedBox(width: 6),
                                      Text(
                                        '${(_sensor!['risk_level'] ?? 'LOW').toUpperCase()} RISK',
                                        style: TextStyle(
                                          color: _riskColor(_sensor!['risk_level']),
                                          fontWeight: FontWeight.bold,
                                          fontSize: 12,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ] else ...[
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: const Center(
                              child: Text('No sensor data yet', style: TextStyle(color: Colors.grey)),
                            ),
                          ),
                        ],
                        const SizedBox(height: 80),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _statCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 8)],
        ),
        child: Row(
          children: [
            Container(
              width: 44, height: 44,
              decoration: BoxDecoration(
                color: color.withAlpha(25),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(value, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: color)),
                Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _sensorRow(String emoji, String label, String value, Color color) {
    return Row(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 20)),
        const SizedBox(width: 12),
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 14)),
        const Spacer(),
        Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }
}
