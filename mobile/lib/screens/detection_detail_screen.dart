import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'dart:convert';

class DetectionDetailScreen extends StatefulWidget {
  final Map<String, dynamic> detection;
  const DetectionDetailScreen({super.key, required this.detection});

  @override
  State<DetectionDetailScreen> createState() => _DetectionDetailScreenState();
}

class _DetectionDetailScreenState extends State<DetectionDetailScreen> {
  late Map<String, dynamic> _detection;
  bool _updating = false;

  @override
  void initState() {
    super.initState();
    _detection = Map<String, dynamic>.from(widget.detection);
    _loadDetails();
  }

  Future<void> _loadDetails() async {
    final id = _detection['id'];
    if (id == null) return;
    try {
      final res = await ApiService.get('/disease/detections/$id');
      if (res.statusCode == 200 && mounted) {
        setState(() => _detection = jsonDecode(res.body));
      }
    } catch (_) {}
  }

  Future<void> _updateStatus(String status) async {
    setState(() => _updating = true);
    try {
      final res = await ApiService.patch(
        '/disease/detections/${_detection['id']}/status',
        {'status': status},
      );
      if (res.statusCode == 200 && mounted) {
        setState(() {
          _detection['status'] = status;
          _updating = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Marked as $status'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (_) {
      setState(() => _updating = false);
    }
  }

  Color _severityColor(String? s) {
    switch (s) {
      case 'critical': return Colors.red;
      case 'high': return Colors.orange;
      case 'medium': return Colors.amber;
      default: return Colors.green;
    }
  }

  Color _statusColor(String? s) {
    switch (s) {
      case 'active': return Colors.red;
      case 'treated': return Colors.orange;
      case 'resolved': return Colors.green;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final sev = _detection['severity'] ?? 'low';
    final status = _detection['status'] ?? 'active';
    final sevColor = _severityColor(sev);
    final conf = (_detection['confidence_score'] ?? 0).toDouble();
    final disease = _detection['disease_name'] ?? 'Unknown';
    final zone = _detection['zone_code'] ?? '-';
    final diseaseDetails = _detection['disease_details'];

    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: const Text('Detection Details', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 8)],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                          color: sevColor.withAlpha(30),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: const Center(child: Text('🦠', style: TextStyle(fontSize: 30))),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(disease,
                                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 4),
                            Text('Zone $zone',
                                style: const TextStyle(color: Colors.grey, fontSize: 13)),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          _badge(sev.toUpperCase(), sevColor),
                          const SizedBox(height: 6),
                          _badge(status.toUpperCase(), _statusColor(status)),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Confidence
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('AI Confidence', style: TextStyle(fontSize: 13, color: Colors.grey)),
                      Text('${conf.toStringAsFixed(1)}%',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: sevColor)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: LinearProgressIndicator(
                      value: conf / 100,
                      backgroundColor: Colors.grey.shade200,
                      color: sevColor,
                      minHeight: 8,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // Disease info
            if (diseaseDetails != null) ...[
              _sectionTitle('About This Disease'),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6)],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (diseaseDetails['description'] != null) ...[
                      Text(diseaseDetails['description'],
                          style: const TextStyle(fontSize: 14, height: 1.5, color: Color(0xFF374151))),
                      const SizedBox(height: 14),
                    ],
                    if (diseaseDetails['symptoms'] != null) ...[
                      _infoRow(Icons.sick_outlined, 'Symptoms', diseaseDetails['symptoms'], Colors.orange),
                      const SizedBox(height: 10),
                    ],
                    if (diseaseDetails['causes'] != null)
                      _infoRow(Icons.bug_report_outlined, 'Cause', diseaseDetails['causes'], Colors.red),
                  ],
                ),
              ),
              const SizedBox(height: 14),
            ],

            // Treatment
            _sectionTitle('Treatment Recommendation'),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF4CAF50).withAlpha(100)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('💊', style: TextStyle(fontSize: 24)),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      diseaseDetails?['treatment'] ??
                          'Monitor closely and apply appropriate fungicide. Consult an agronomist for specific treatment.',
                      style: const TextStyle(fontSize: 14, height: 1.5, color: Color(0xFF1B5E20)),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            // Detection metadata
            _sectionTitle('Detection Info'),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6)],
              ),
              child: Column(
                children: [
                  _metaRow('Zone', 'Zone $zone'),
                  _metaRow('Severity', sev.toUpperCase()),
                  _metaRow('Status', status.toUpperCase()),
                  _metaRow('Confidence', '${conf.toStringAsFixed(1)}%'),
                  if (_detection['detected_at'] != null)
                    _metaRow('Detected', _formatDate(_detection['detected_at'])),
                  if (_detection['resolved_at'] != null)
                    _metaRow('Resolved', _formatDate(_detection['resolved_at'])),
                ],
              ),
            ),

            // Action buttons
            if (status == 'active') ...[
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _updating ? null : () => _updateStatus('treated'),
                      icon: const Icon(Icons.medical_services_outlined),
                      label: const Text('Mark Treated'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.orange,
                        side: const BorderSide(color: Colors.orange),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        minimumSize: const Size(0, 48),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _updating ? null : () => _updateStatus('resolved'),
                      icon: const Icon(Icons.check_circle_outline),
                      label: const Text('Resolved'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2E7D32),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        minimumSize: const Size(0, 48),
                      ),
                    ),
                  ),
                ],
              ),
            ],
            if (status == 'treated') ...[
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton.icon(
                  onPressed: _updating ? null : () => _updateStatus('resolved'),
                  icon: const Icon(Icons.check_circle_outline),
                  label: const Text('Mark as Resolved'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2E7D32),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _badge(String text, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(
      color: color.withAlpha(25),
      borderRadius: BorderRadius.circular(20),
    ),
    child: Text(text, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold)),
  );

  Widget _sectionTitle(String title) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: Text(title,
        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF1a1a1a))),
  );

  Widget _infoRow(IconData icon, String label, String value, Color color) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Icon(icon, size: 18, color: color),
      const SizedBox(width: 8),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.bold)),
            Text(value, style: const TextStyle(fontSize: 13, color: Color(0xFF374151))),
          ],
        ),
      ),
    ],
  );

  Widget _metaRow(String label, String value) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
      ],
    ),
  );

  String _formatDate(String iso) {
    try {
      final dt = DateTime.parse(iso).toLocal();
      final months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      return '${months[dt.month - 1]} ${dt.day}, ${dt.year} ${dt.hour.toString().padLeft(2,'0')}:${dt.minute.toString().padLeft(2,'0')}';
    } catch (_) { return iso; }
  }
}
