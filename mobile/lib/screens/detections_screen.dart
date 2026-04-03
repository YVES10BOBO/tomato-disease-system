import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'detection_detail_screen.dart';

class DetectionsScreen extends StatefulWidget {
  const DetectionsScreen({super.key});
  @override
  State<DetectionsScreen> createState() => _DetectionsScreenState();
}

class _DetectionsScreenState extends State<DetectionsScreen> {
  List<dynamic> _detections = [];
  String? _farmId;
  bool _loading = true;
  String _filter = 'all';

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
      final res = await ApiService.get('/disease/$_farmId/detections?limit=50');
      setState(() {
        if (res.statusCode == 200) _detections = jsonDecode(res.body)['detections'] ?? [];
        _loading = false;
      });
    } catch (_) { setState(() => _loading = false); }
  }

  Color _severityColor(String? s) {
    switch (s) {
      case 'critical': return Colors.red;
      case 'high': return Colors.orange;
      case 'medium': return Colors.amber;
      default: return Colors.green;
    }
  }

  List<dynamic> get _filtered {
    if (_filter == 'active') return _detections.where((d) => d['status'] == 'active').toList();
    if (_filter == 'resolved') return _detections.where((d) => d['status'] == 'resolved').toList();
    return _detections;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: const Text('Detections', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32)))
          : Column(
              children: [
                // Filter chips
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: ['all', 'active', 'resolved'].map((f) =>
                      Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          label: Text(f.toUpperCase(), style: const TextStyle(fontSize: 11)),
                          selected: _filter == f,
                          onSelected: (_) => setState(() => _filter = f),
                          selectedColor: const Color(0xFF2E7D32).withAlpha(50),
                          checkmarkColor: const Color(0xFF2E7D32),
                        ),
                      ),
                    ).toList(),
                  ),
                ),
                Expanded(
                  child: _filtered.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Text('🔬', style: TextStyle(fontSize: 48)),
                              const SizedBox(height: 12),
                              Text('No $_filter detections', style: const TextStyle(color: Colors.grey)),
                            ],
                          ),
                        )
                      : RefreshIndicator(
                          onRefresh: _loadData,
                          color: const Color(0xFF2E7D32),
                          child: ListView.builder(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            itemCount: _filtered.length,
                            itemBuilder: (_, i) {
                              final d = _filtered[i];
                              final sev = d['severity'] ?? 'low';
                              final color = _severityColor(sev);
                              return GestureDetector(
                                onTap: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => DetectionDetailScreen(detection: d),
                                  ),
                                ),
                                child: Container(
                                margin: const EdgeInsets.only(bottom: 10),
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(16),
                                  boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6)],
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.all(10),
                                          decoration: BoxDecoration(
                                            color: color.withAlpha(25),
                                            borderRadius: BorderRadius.circular(10),
                                          ),
                                          child: const Text('🦠', style: TextStyle(fontSize: 22)),
                                        ),
                                        const SizedBox(width: 12),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(d['disease_name'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                                              Text('Zone ${d['zone_code']} · ${d['confidence_score']}% confidence',
                                                style: const TextStyle(color: Colors.grey, fontSize: 12)),
                                            ],
                                          ),
                                        ),
                                        Column(
                                          crossAxisAlignment: CrossAxisAlignment.end,
                                          children: [
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                              decoration: BoxDecoration(
                                                color: color.withAlpha(25),
                                                borderRadius: BorderRadius.circular(20),
                                              ),
                                              child: Text(sev, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold)),
                                            ),
                                            const SizedBox(height: 4),
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                              decoration: BoxDecoration(
                                                color: d['status'] == 'active' ? Colors.red.withAlpha(25) : Colors.green.withAlpha(25),
                                                borderRadius: BorderRadius.circular(20),
                                              ),
                                              child: Text(d['status'] ?? '',
                                                style: TextStyle(
                                                  color: d['status'] == 'active' ? Colors.red : Colors.green,
                                                  fontSize: 11, fontWeight: FontWeight.bold,
                                                )),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 10),
                                    // Confidence bar
                                    ClipRRect(
                                      borderRadius: BorderRadius.circular(4),
                                      child: LinearProgressIndicator(
                                        value: (d['confidence_score'] ?? 0) / 100,
                                        backgroundColor: Colors.grey.shade200,
                                        color: color,
                                        minHeight: 4,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                            },
                          ),
                        ),
                ),
              ],
            ),
    );
  }
}
