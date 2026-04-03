import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});
  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  List<dynamic> _alerts = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final res = await ApiService.get('/alerts/?limit=100');
      setState(() {
        if (res.statusCode == 200) _alerts = jsonDecode(res.body)['alerts'] ?? [];
        _loading = false;
      });
    } catch (_) { setState(() => _loading = false); }
  }

  Future<void> _markRead(String id) async {
    await ApiService.put('/alerts/$id/read', {});
    setState(() {
      final i = _alerts.indexWhere((a) => a['id'] == id);
      if (i != -1) _alerts[i] = {..._alerts[i], 'is_read': true};
    });
  }

  Future<void> _markAllRead() async {
    final unread = _alerts.where((a) => !a['is_read']).toList();
    await Future.wait(unread.map((a) => ApiService.put('/alerts/${a['id']}/read', {})));
    setState(() {
      _alerts = _alerts.map((a) => {...a, 'is_read': true}).toList();
    });
  }

  Color _riskColor(String? r) {
    switch (r?.toLowerCase()) {
      case 'critical': return Colors.red;
      case 'high': return Colors.orange;
      case 'medium': return Colors.amber;
      default: return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {
    final unreadCount = _alerts.where((a) => !a['is_read']).length;
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: Row(
          children: [
            const Text('Alerts', style: TextStyle(fontWeight: FontWeight.bold)),
            if (unreadCount > 0) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(color: Colors.red, borderRadius: BorderRadius.circular(12)),
                child: Text('$unreadCount', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
              ),
            ],
          ],
        ),
        actions: [
          if (unreadCount > 0)
            TextButton(
              onPressed: _markAllRead,
              child: const Text('Mark all read', style: TextStyle(color: Colors.white, fontSize: 12)),
            ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32)))
          : _alerts.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('🎉', style: TextStyle(fontSize: 56)),
                      SizedBox(height: 12),
                      Text('No alerts — all clear!', style: TextStyle(color: Colors.grey, fontSize: 16)),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadData,
                  color: const Color(0xFF2E7D32),
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _alerts.length,
                    itemBuilder: (_, i) {
                      final a = _alerts[i];
                      final isRead = a['is_read'] ?? false;
                      final color = _riskColor(a['risk_level']);
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        decoration: BoxDecoration(
                          color: isRead ? Colors.white : Colors.orange.shade50,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: isRead ? Colors.transparent : Colors.orange.shade200,
                          ),
                          boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4)],
                        ),
                        child: ListTile(
                          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          leading: Stack(
                            children: [
                              Container(
                                width: 44, height: 44,
                                decoration: BoxDecoration(
                                  color: color.withAlpha(25),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Center(child: Text('🔔', style: TextStyle(fontSize: 20))),
                              ),
                              if (!isRead)
                                Positioned(
                                  top: 0, right: 0,
                                  child: Container(width: 10, height: 10,
                                    decoration: const BoxDecoration(color: Colors.orange, shape: BoxShape.circle),
                                  ),
                                ),
                            ],
                          ),
                          title: Text(
                            a['title'] ?? '',
                            style: TextStyle(
                              fontWeight: isRead ? FontWeight.normal : FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 3),
                              Text(a['message'] ?? '', style: const TextStyle(fontSize: 12, color: Colors.grey), maxLines: 2, overflow: TextOverflow.ellipsis),
                              const SizedBox(height: 4),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: color.withAlpha(25),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Text(
                                  (a['risk_level'] ?? 'low').toUpperCase(),
                                  style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
                                ),
                              ),
                            ],
                          ),
                          trailing: !isRead
                              ? IconButton(
                                  icon: const Icon(Icons.check_circle_outline, color: Colors.green),
                                  onPressed: () => _markRead(a['id']),
                                  tooltip: 'Mark as read',
                                )
                              : const Icon(Icons.check_circle, color: Colors.green, size: 20),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
