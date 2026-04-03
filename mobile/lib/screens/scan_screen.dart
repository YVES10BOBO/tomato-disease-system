import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import '../services/api_service.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  File? _image;
  bool _analyzing = false;
  Map<String, dynamic>? _result;
  String? _farmId;
  String _zoneCode = 'A1';
  String _error = '';
  final _picker = ImagePicker();

  final List<String> _zones = ['A1','A2','A3','A4','B1','B2','B3','B4','C1','C2','C3','C4','D1','D2','D3','D4'];

  @override
  void initState() {
    super.initState();
    _loadFarm();
  }

  Future<void> _loadFarm() async {
    try {
      final res = await ApiService.get('/farms/');
      if (res.statusCode == 200) {
        final farms = jsonDecode(res.body)['farms'];
        if (farms != null && farms.isNotEmpty) {
          setState(() => _farmId = farms[0]['id']);
        }
      }
    } catch (_) {}
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(source: source, imageQuality: 85, maxWidth: 1024);
      if (picked != null) {
        setState(() { _image = File(picked.path); _result = null; _error = ''; });
      }
    } catch (e) {
      setState(() => _error = 'Could not access camera/gallery. Check permissions.');
    }
  }

  Future<void> _analyze() async {
    if (_image == null) return;
    if (_farmId == null) {
      setState(() => _error = 'No farm found. Create a farm first.');
      return;
    }
    setState(() { _analyzing = true; _error = ''; _result = null; });

    try {
      final token = await ApiService.getToken();
      final req = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiService.baseUrl}/disease/predict'),
      );
      if (token != null) req.headers['Authorization'] = 'Bearer $token';
      req.fields['farm_id'] = _farmId!;
      req.fields['zone_code'] = _zoneCode;
      req.files.add(await http.MultipartFile.fromPath('file', _image!.path));

      final streamed = await req.send();
      final res = await http.Response.fromStream(streamed);

      if (res.statusCode == 200) {
        setState(() { _result = jsonDecode(res.body); _analyzing = false; });
      } else if (res.statusCode == 404 || res.statusCode == 405) {
        setState(() {
          _error = 'AI model not yet deployed. Results will appear when the model is installed on the server.';
          _analyzing = false;
        });
      } else {
        final err = jsonDecode(res.body);
        setState(() { _error = err['detail'] ?? 'Analysis failed'; _analyzing = false; });
      }
    } catch (e) {
      setState(() { _error = 'Connection failed. Make sure the backend is running.'; _analyzing = false; });
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: const Text('Scan Leaf', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Instruction banner
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F5E9),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFF4CAF50).withAlpha(100)),
              ),
              child: const Row(
                children: [
                  Text('📸', style: TextStyle(fontSize: 22)),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Take a clear photo of the tomato leaf or plant showing symptoms. Good lighting improves accuracy.',
                      style: TextStyle(fontSize: 12, color: Color(0xFF1B5E20)),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Zone selector
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6)],
              ),
              child: Row(
                children: [
                  const Icon(Icons.grid_view, color: Color(0xFF2E7D32)),
                  const SizedBox(width: 10),
                  const Text('Farm Zone:', style: TextStyle(fontWeight: FontWeight.w600)),
                  const SizedBox(width: 12),
                  Expanded(
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _zoneCode,
                        isExpanded: true,
                        onChanged: (v) => setState(() => _zoneCode = v!),
                        items: _zones.map((z) => DropdownMenuItem(
                          value: z,
                          child: Text('Zone $z'),
                        )).toList(),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Image area
            GestureDetector(
              onTap: () => _showImageSourceSheet(),
              child: Container(
                width: double.infinity,
                height: 260,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: _image != null
                        ? const Color(0xFF2E7D32)
                        : Colors.grey.shade300,
                    width: _image != null ? 2 : 1,
                  ),
                  boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6)],
                ),
                child: _image != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(18),
                        child: Image.file(_image!, fit: BoxFit.cover),
                      )
                    : Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.add_a_photo_outlined, size: 52, color: Colors.grey.shade400),
                          const SizedBox(height: 12),
                          Text('Tap to take or choose photo',
                              style: TextStyle(color: Colors.grey.shade500, fontSize: 14)),
                          const SizedBox(height: 4),
                          Text('JPG, PNG supported',
                              style: TextStyle(color: Colors.grey.shade400, fontSize: 12)),
                        ],
                      ),
              ),
            ),

            if (_image != null) ...[
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton.icon(
                    onPressed: () => _showImageSourceSheet(),
                    icon: const Icon(Icons.refresh, size: 16),
                    label: const Text('Change photo'),
                    style: TextButton.styleFrom(foregroundColor: const Color(0xFF2E7D32)),
                  ),
                ],
              ),
            ],

            const SizedBox(height: 16),

            // Error
            if (_error.isNotEmpty)
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.warning_amber_outlined, color: Colors.orange.shade700, size: 18),
                    const SizedBox(width: 8),
                    Expanded(child: Text(_error,
                        style: TextStyle(color: Colors.orange.shade800, fontSize: 13))),
                  ],
                ),
              ),

            // Analyze button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: (_image == null || _analyzing) ? null : _analyze,
                icon: _analyzing
                    ? const SizedBox(width: 20, height: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Icon(Icons.biotech),
                label: Text(
                  _analyzing ? 'Analyzing...' : 'Analyze Leaf',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2E7D32),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  disabledBackgroundColor: Colors.grey.shade300,
                ),
              ),
            ),

            // Result
            if (_result != null) ...[
              const SizedBox(height: 20),
              _buildResult(),
            ],
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildResult() {
    final isHealthy = _result!['is_healthy'] ?? false;
    final disease = _result!['disease_name'] ?? 'Unknown';
    final conf = (_result!['confidence_score'] ?? 0).toDouble();
    final sev = _result!['severity'] ?? 'low';
    final treatment = _result!['treatment'] ?? '';
    final isUnknown = disease == 'Unknown';
    final color = isHealthy ? Colors.green : isUnknown ? Colors.grey : _severityColor(sev);

    if (isUnknown) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.orange.shade50,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.orange.shade200),
        ),
        child: Row(
          children: [
            const Text('📷', style: TextStyle(fontSize: 28)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Not a tomato leaf',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  const SizedBox(height: 4),
                  Text(treatment,
                      style: TextStyle(color: Colors.orange.shade800, fontSize: 13)),
                ],
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 8)],
        border: Border.all(color: color.withAlpha(100), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Result header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withAlpha(25),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Row(
              children: [
                Text(isHealthy ? '✅' : '🦠', style: const TextStyle(fontSize: 32)),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isHealthy ? 'Healthy Plant' : disease,
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color),
                      ),
                      Text(
                        isHealthy
                            ? 'No disease detected'
                            : 'Zone $_zoneCode · ${conf.toStringAsFixed(1)}% confidence',
                        style: const TextStyle(color: Colors.grey, fontSize: 12),
                      ),
                    ],
                  ),
                ),
                if (!isHealthy)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: color.withAlpha(30),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(sev.toUpperCase(),
                        style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold)),
                  ),
              ],
            ),
          ),

          if (!isHealthy) ...[
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Confidence', style: TextStyle(fontSize: 12, color: Colors.grey)),
                      Text('${conf.toStringAsFixed(1)}%',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: color)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: conf / 100,
                      backgroundColor: Colors.grey.shade200,
                      color: color,
                      minHeight: 6,
                    ),
                  ),
                ],
              ),
            ),
          ],

          if (treatment.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Treatment', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8F5E9),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('💊', style: TextStyle(fontSize: 16)),
                        const SizedBox(width: 8),
                        Expanded(child: Text(treatment,
                            style: const TextStyle(fontSize: 13, color: Color(0xFF1B5E20)))),
                      ],
                    ),
                  ),
                ],
              ),
            )
          else
            const SizedBox(height: 16),
        ],
      ),
    );
  }

  void _showImageSourceSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(width: 40, height: 4,
                decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2))),
            const SizedBox(height: 16),
            const Text('Choose Image Source',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ListTile(
              leading: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF2E7D32).withAlpha(25),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.camera_alt, color: Color(0xFF2E7D32)),
              ),
              title: const Text('Take Photo'),
              subtitle: const Text('Use camera to capture leaf'),
              onTap: () { Navigator.pop(context); _pickImage(ImageSource.camera); },
            ),
            ListTile(
              leading: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.blue.withAlpha(25),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.photo_library, color: Colors.blue),
              ),
              title: const Text('Choose from Gallery'),
              subtitle: const Text('Pick an existing photo'),
              onTap: () { Navigator.pop(context); _pickImage(ImageSource.gallery); },
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
