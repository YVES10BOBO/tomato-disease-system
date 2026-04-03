import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SensorsScreen extends StatefulWidget {
  const SensorsScreen({super.key});
  @override
  State<SensorsScreen> createState() => _SensorsScreenState();
}

class _SensorsScreenState extends State<SensorsScreen> {
  Map<String, dynamic>? _latest;
  Map<String, dynamic>? _risk;
  String? _farmId;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final farmRes = await ApiService.get('/farms/');
      if (farmRes.statusCode == 200) {
        final farms = jsonDecode(farmRes.body)['farms'];
        if (farms != null && farms.isNotEmpty) _farmId = farms[0]['id'];
      }
      if (_farmId == null) { setState(() => _loading = false); return; }
      final results = await Future.wait([
        ApiService.get('/iot/sensors/$_farmId/latest'),
        ApiService.get('/iot/sensors/$_farmId/risk'),
      ]);
      setState(() {
        if (results[0].statusCode == 200) _latest = jsonDecode(results[0].body);
        if (results[1].statusCode == 200) {
          final d = jsonDecode(results[1].body);
          _risk = d['risk_analysis'];
        }
        _loading = false;
      });
    } catch (_) { setState(() => _loading = false); }
  }

  Color _riskColor(String? r) {
    switch (r?.toLowerCase()) {
      case 'critical': return Colors.red;
      case 'high': return Colors.orange;
      case 'medium': return Colors.amber;
      default: return const Color(0xFF2E7D32);
    }
  }

  @override
  Widget build(BuildContext context) {
    final risk = _latest?['risk_level'] ?? 'low';
    final riskColor = _riskColor(risk);

    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: const Text('IoT Sensors', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32)))
          : RefreshIndicator(
              onRefresh: _loadData,
              color: const Color(0xFF2E7D32),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Risk Banner
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: riskColor,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Environmental Risk', style: TextStyle(color: Colors.white70, fontSize: 12)),
                                const SizedBox(height: 4),
                                Text(risk.toUpperCase(), style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ),
                          Text(
                            risk == 'low' ? '✅' : risk == 'medium' ? '⚠️' : risk == 'high' ? '🔥' : '🚨',
                            style: const TextStyle(fontSize: 44),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Sensor Cards
                    if (_latest != null) ...[
                      _sensorCard('🌡️', 'Temperature', '${_latest!['temperature']}', '°C',
                        'Normal: 18–30°C',
                        _latest!['temperature'] > 30 || _latest!['temperature'] < 18 ? Colors.orange : const Color(0xFF2E7D32)),
                      const SizedBox(height: 10),
                      _sensorCard('💧', 'Humidity', '${_latest!['humidity']}', '%',
                        'Normal: 60–80%',
                        _latest!['humidity'] > 85 || _latest!['humidity'] < 50 ? Colors.blue.shade700 : const Color(0xFF2E7D32)),
                      const SizedBox(height: 10),
                      _sensorCard('🌱', 'Soil Moisture', '${_latest!['soil_moisture']}', '%',
                        'Normal: 40–70%',
                        _latest!['soil_moisture'] > 80 || _latest!['soil_moisture'] < 30 ? Colors.orange : const Color(0xFF2E7D32)),
                      const SizedBox(height: 16),
                    ],

                    // Risk Analysis
                    if (_risk != null) ...[
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Risk Analysis', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 12),
                            if (_risk!['risks'] != null && (_risk!['risks'] as List).isNotEmpty)
                              ...(_risk!['risks'] as List).map((r) => Container(
                                margin: const EdgeInsets.only(bottom: 8),
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.orange.shade50,
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: Colors.orange.shade200),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text('⚠ ${r['disease']}', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.orange.shade800, fontSize: 13)),
                                    const SizedBox(height: 4),
                                    Text(r['action'] ?? '', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                  ],
                                ),
                              ))
                            else
                              const Text('No active disease risks detected', style: TextStyle(color: Colors.green, fontSize: 13)),
                            if (_risk!['summary'] != null) ...[
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.all(10),
                                decoration: BoxDecoration(color: Colors.grey.shade50, borderRadius: BorderRadius.circular(8)),
                                child: Text(_risk!['summary'], style: const TextStyle(fontSize: 12, color: Colors.grey)),
                              ),
                            ],
                          ],
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

  Widget _sensorCard(String emoji, String label, String value, String unit, String hint, Color color) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6)],
      ),
      child: Row(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 32)),
          const SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
              Text(hint, style: const TextStyle(color: Colors.grey, fontSize: 11)),
            ],
          ),
          const Spacer(),
          Text(value, style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: color)),
          Text(unit, style: const TextStyle(fontSize: 16, color: Colors.grey)),
        ],
      ),
    );
  }
}
