# TomatoGuard - Quick Reference Guide

## 📱 MOBILE APP (7 Screens)

```
┌─────────────────────────────────────────────────────────┐
│                    MOBILE APP SCREENS                   │
├─────────────────────────────────────────────────────────┤

1️⃣  LOGIN/REGISTER
    • Email & Password
    • JWT Token Storage
    • Auto-login after register

2️⃣  DASHBOARD (Home) 
    • Farm Health Status (Green/Yellow/Red)
    • Real-time Sensors (Temp/Humidity/Soil)
    • Recent Alerts (Last 5)
    • Quick Actions (Scan/History/Alerts)
    • 5-Tab Bottom Navigation

3️⃣  SCAN SCREEN
    • Camera or Gallery Upload
    • 3-5 second countdown
    • Auto-analysis
    • Results: Disease + Confidence + Treatment
    • Save Detection

4️⃣  HISTORY SCREEN
    • Tab 1: Past Detections (Disease History)
    • Tab 2: Sensor Graphs (Temp/Humidity/Soil)
    • Tab 3: Alert History (Notifications)
    • Sortable, Filterable, Exportable

5️⃣  ALERTS SCREEN
    • Active Alerts List (Newest first)
    • Color-coded by severity
    • Mark as Read/Dismiss
    • Quick links to details

6️⃣  SETTINGS SCREEN
    • Profile (Edit Name/Phone/Avatar)
    • Notifications (Toggle types)
    • Farm Settings (Zone/Location)
    • App Preferences (Theme/Language)
    • Security (Change Password)
    • Logout

7️⃣  BOTTOM NAVIGATION
    • 🏠 Dashboard
    • 📷 Scan
    • 📊 History
    • ⚠️ Alerts
    • ⚙️ Settings

```

---

## 🖥️ WEB DASHBOARD (7 Pages)

```
┌─────────────────────────────────────────────────────────┐
│                  WEB DASHBOARD PAGES                    │
├─────────────────────────────────────────────────────────┤

1️⃣  DASHBOARD (Overview)
    ┌─────────────────────────────────┐
    │ Summary Cards:                  │
    │ • Healthy Zones ✅              │
    │ • Affected Zones ❌             │
    │ • Active Alerts 🚨              │
    │ • Avg Conditions 🌡️             │
    └─────────────────────────────────┘
    ┌─────────────────────────────────┐
    │ Zone Health Map (A1-D4):        │
    │ 🟢 Green = Healthy              │
    │ 🟡 Yellow = Medium Risk         │
    │ 🔴 Red = Critical/Disease       │
    └─────────────────────────────────┘
    ┌─────────────────────────────────┐
    │ Live Graphs:                    │
    │ • Temperature (24h)             │
    │ • Humidity (24h)                │
    │ • Soil Moisture (24h)           │
    └─────────────────────────────────┘
    ┌─────────────────────────────────┐
    │ Recent Activity:                │
    │ • Latest Detections             │
    │ • Active Alerts                 │
    └─────────────────────────────────┘

2️⃣  ZONES MANAGEMENT
    • 16-zone grid (A1-D4)
    • Click zone → Details
    • Zone Health Status
    • Last sensor readings
    • Active diseases
    • Assigned technician
    • Zone-specific graphs

3️⃣  DISEASE DETECTION
    • Filterable table of all detections
    • Filters: Disease/Date/Zone/Severity/Status
    • Click row → Full Details
    • Details show:
      - Leaf image
      - Disease info + confidence
      - Treatment recommendation
      - Status management
      - Bulk export (CSV/PDF)

4️⃣  ALERTS MANAGEMENT
    • Alert summary (Total/Critical/Medium/Low)
    • Filter by type/status/date
    • Alert list (color-coded by severity)
    • Mark as read/resolved
    • Linked to detection/zone
    • Real-time notifications
    • Alert history

5️⃣  ANALYTICS & REPORTS
    • Disease Statistics (Pie chart)
    • Detection Trends (Line chart)
    • Risk Analysis
    • Zone Performance Comparison
    • Treatment Effectiveness
    • Generate Reports (PDF/Excel)
    • Schedule automated reports
    • Predictive analytics

6️⃣  TEAM MANAGEMENT
    • User list (sortable/filterable)
    • User details:
      - Profile info
      - Role assignment
      - Farm assignments
      - Zone assignments
      - Active/inactive status
    • Invite new technician
    • Reset password
    • Activity logs
    • Deactivate/delete user

7️⃣  SETTINGS
    • Personal: Profile/Password/Notifications
    • Farm: Farm info/zones/assignments
    • System (Admin only):
      - API configuration
      - Database settings
      - Security
      - Email settings
      - Logs
      - Backup/restore

```

---

## 👥 USER ROLES & ACCESS

```
┌──────────────────────────────────────────────────────────┐
│                      USER ROLES                          │
├──────────────────────────────────────────────────────────┤

🌾 FARMER (Personal Farm Only)
├─ Can: View own farm, Scan, View history, See alerts
├─ Cannot: Access other farms, Manage users, Admin panel
└─ Mobile: All features | Web: Basic pages only

🔧 TECHNICIAN (Assigned Farms Only)
├─ Can: View assigned farms, Scan, Record treatment
├─ Can: Generate reports, Manage zones
├─ Cannot: Access unassigned farms, Manage other users
└─ Mobile: All features | Web: Farm + History + Alerts

👨‍💼 FARM MANAGER (All Organization Farms)
├─ Can: View all farms, Manage technicians
├─ Can: Manage zones, View analytics
├─ Can: Assign technicians, Invite users
├─ Cannot: Access system admin functions
└─ Mobile: Dashboard only | Web: All except System Settings

🔐 ADMIN (Entire System)
├─ Can: View everything, Manage all users
├─ Can: Change roles, Access logs, Manage database
├─ Can: Manage disease database, Export all data
└─ Mobile: Limited | Web: All features including Admin

┌──────────────────────────────────────────────────────────┐
│                   DATA VISIBILITY                        │
├──────────────────────────────────────────────────────────┤
Farmer          → Own farm data only
Technician      → Assigned farm(s) data only
Farm Manager    → All farms in organization
Admin           → All data in system
```

---

## 🔄 DATA FLOW (Simplified)

```
IoT DEVICE (ESP32-CAM)
│
├─ Every 10s: POST /iot/sensors
│  └─ {farm_id, temperature, humidity, soil_moisture}
│
└─ Every 60s: POST /disease/predict
   └─ {file: image, farm_id, zone_code}

                    ↓

         FASTAPI BACKEND (Process Data)
         │
         ├─ Store sensor readings
         ├─ Run AI model on image
         ├─ Calculate risk level
         ├─ Create alerts if needed
         └─ Save detection results

                    ↓

          SUPABASE DATABASE (Store)
          │
          ├─ sensor_logs
          ├─ detections
          ├─ alerts
          ├─ users
          ├─ farms
          └─ zones

                    ↓

    ┌────────────────┬────────────────┐
    ↓                ↓
MOBILE APP      WEB DASHBOARD
│               │
├─ Dashboard    ├─ Dashboard
├─ Scan         ├─ Zones
├─ History      ├─ Detections
├─ Alerts       ├─ Alerts
└─ Settings     ├─ Analytics
                ├─ Team Mgmt
                └─ Settings
```

---

## 📊 COMPONENT MATRIX

```
┌────────────────────────────────────────────────────────────┐
│             WHAT EACH PAGE SHOWS                           │
├────────────────────────────────────────────────────────────┤

                    Mobile    |  Web Dashboard
────────────────────────────────────────────────────────────
Dashboard          ✅ Data   |  ✅ Overview
Scan               ✅ Camera |  ❌ N/A
History            ✅ Graphs |  ✅ Tables/Charts
Detections         ⭐ Alert |  ✅ Full Table
Alerts             ✅ List   |  ✅ Management
Zones              ⭐ Alert |  ✅ Map + Details
Analytics          ❌ N/A    |  ✅ Reports
Team Mgmt          ❌ N/A    |  ✅ User List
Settings           ✅ Basic  |  ✅ Full Config

✅ = Full feature
⭐ = Limited view (notification only)
❌ = Not available
```

---

## 🎯 KEY FEATURES BY SCREEN

```
LOGIN/REGISTER
├─ Email validation
├─ Password strength check
├─ JWT token generation
└─ Auto-login after register

DASHBOARD (Mobile)
├─ Real-time sensor display
├─ Health status indicator
├─ Recent alerts (5 latest)
├─ Quick action buttons
└─ Auto-refresh (10 seconds)

DASHBOARD (Web)
├─ Summary cards (4 metrics)
├─ Zone health map (16 zones)
├─ 24-hour sensor graphs (3)
├─ Recent detections table
├─ Active alerts list
└─ Customizable widgets

SCAN
├─ Camera preview + capture
├─ Gallery selection
├─ 3-5 second auto-countdown
├─ AI disease detection
├─ Confidence score display
├─ Treatment recommendations
└─ Save/share options

HISTORY (Mobile)
├─ Detection records
├─ Sensor graphs
├─ Alert history
├─ Date/disease filters
└─ Export to CSV

HISTORY (Web)
├─ Searchable detection table
├─ Interactive sensor charts
├─ Alert timeline
├─ Date range filtering
├─ Severity filtering
├─ Zone filtering
└─ Bulk export (CSV/PDF)

ALERTS
├─ Severity badges (Red/Orange/Yellow)
├─ Auto-sort by urgency
├─ Mark as read/resolved
├─ Link to detection
├─ Push notifications
├─ Sound alerts (if enabled)
└─ Auto-dismiss after 24h

ZONES (Web)
├─ 16-zone visual grid
├─ Color-coded health
├─ Last reading display
├─ Disease count
├─ Technician assignment
├─ Click for details
└─ Zone-specific graphs

ANALYTICS (Web)
├─ Disease pie chart
├─ Detection trend line
├─ Risk correlation analysis
├─ Zone comparison
├─ Treatment effectiveness
├─ Report generation
└─ Predictive forecasting

TEAM MGMT (Web)
├─ User directory
├─ Role assignment
├─ Farm assignment
├─ Zone assignment
├─ Password reset
├─ User activation/deactivation
└─ Activity logs

SETTINGS
├─ Profile editing
├─ Notification preferences
├─ Theme/language selection
├─ Password change
├─ Account deletion
└─ Logout
```

---

## 🔐 SECURITY & PERMISSIONS

```
Authentication:
├─ Email + Password login
├─ JWT token generation
├─ Token stored in device/browser
└─ Token expires (refreshable)

Authorization:
├─ Role-based access control (RBAC)
├─ Farmer: Own farm only
├─ Technician: Assigned farms only
├─ Manager: All farm data
├─ Admin: All system data
└─ Invalid requests return 401/403

Data Privacy:
├─ Users see only their data
├─ Technicians see only assigned farms
├─ Managers see organization data
├─ Admin sees all data
└─ Passwords hashed (never stored plaintext)

Encryption:
├─ HTTPS for all connections
├─ Ngrok tunnel for development
├─ Database passwords encrypted
└─ JWT tokens signed
```

---

## 📱 MOBILE APP PAGES SUMMARY

| Screen | Purpose | Shows | Actions |
|--------|---------|-------|---------|
| **Login** | Authentication | Form | Login/Register |
| **Dashboard** | Overview | Status+Sensors | Scan/History/Alerts |
| **Scan** | Disease Detection | Camera/Gallery | Capture/Analyze |
| **History** | Past Data | Graphs/Records | Filter/Export |
| **Alerts** | Notifications | Alert List | Mark Read/Dismiss |
| **Settings** | Preferences | Config Options | Edit/Save |

---

## 🖥️ WEB DASHBOARD PAGES SUMMARY

| Page | Purpose | Shows | Actions |
|------|---------|-------|---------|
| **Dashboard** | Overview | Summary+Map+Graphs | Refresh/Export |
| **Zones** | Zone Management | 16 Zones Grid | Click Zone/View Details |
| **Detections** | Disease Records | Filterable Table | Filter/Sort/Details |
| **Alerts** | Alert Management | Alert List | Filter/Mark/Resolve |
| **Analytics** | Reports & Trends | Charts & Stats | Filter/Export/Schedule |
| **Team Mgmt** | User Management | User List | Edit/Invite/Reset |
| **Settings** | Configuration | Options | Save/Change |

---

## 🚀 QUICK START

```
For Farmer:
1. Download mobile app
2. Register/Login
3. Allow camera access
4. Go to Scan tab
5. Capture leaf photos
6. View results & alerts

For Technician:
1. Register on web dashboard
2. Login with credentials
3. View assigned farms
4. Check alerts & detections
5. Record treatments
6. Generate reports

For Farm Manager:
1. Create account on web
2. Add farms & zones
3. Invite technicians
4. View all farm data
5. Analyze trends
6. Export reports

For Admin:
1. Access system admin panel
2. Manage all users
3. Configure system
4. Monitor logs
5. Backup data
6. Manage disease database
```

---

**Version:** 1.0 Quick Reference
**Last Updated:** June 2026
**All Components Integrated** ✅
