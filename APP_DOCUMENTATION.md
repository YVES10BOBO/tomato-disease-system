# TomatoGuard - Complete App Documentation

## 📱 MOBILE APP OVERVIEW

**Platform:** Flutter (Cross-platform: iOS & Android)
**Purpose:** Real-time tomato disease detection and monitoring for farmers
**Users:** Farmers, Agricultural Technicians

---

## 🗂️ MOBILE APP - SCREENS & COMPONENTS

### **1. LOGIN SCREEN** 🔐
**Purpose:** Authenticate user before accessing the app
**User Role Required:** Any (Farmer, Technician)

**Components:**
- 📧 Email Input Field
- 🔑 Password Input Field
- 🔘 Login Button
- 📝 "Don't have account?" → Register Link
- ❓ "Forgot Password?" → Password Reset Link
- 🏢 Company Logo

**Functionality:**
- Validates email format
- Validates password (min 6 characters)
- Sends POST /auth/login request
- Stores JWT token in device storage
- Navigates to Dashboard on success
- Shows error message on failed login

**Data Flow:**
```
User Input → Validation → HTTP POST /auth/login → Get JWT Token → Save Token → Navigate
```

---

### **2. REGISTER SCREEN** ✍️
**Purpose:** Create new farmer account
**User Role Required:** New/Unregistered User

**Components:**
- 👤 Full Name Input Field
- 📧 Email Input Field
- 📱 Phone Number Input Field
- 🔑 Password Input Field
- 🔑 Confirm Password Input Field
- 🎯 Role Selection (Farmer/Technician)
- 🔘 Register Button
- 🔗 "Already have account?" → Login Link

**Functionality:**
- Validates all fields before submission
- Password strength validation (min 6 chars, mix of letters/numbers)
- Phone number validation (Rwanda format)
- Sends POST /auth/register request
- Automatically logs in after registration
- Stores token and redirects to Dashboard

**Data Flow:**
```
User Input → Validation → HTTP POST /auth/register → Get Token → Auto Login → Dashboard
```

---

### **3. DASHBOARD SCREEN** 📊
**Purpose:** Main hub - Overview of farm health, alerts, and quick actions
**User Role Required:** Authenticated (Farmer or Technician)
**Access:** Everyone who logs in

**Components:**

#### **Top Section - Farm Overview**
- 🌾 Farm Name (Editable)
- 📍 Selected Zone/Location
- ⏰ Last Update Time
- 🔄 Refresh Button

#### **Health Status Card** (Main Display)
- 🟢 **GREEN** = All Healthy (No disease detected)
- 🟡 **YELLOW** = Medium Risk (Monitor closely)
- 🔴 **RED** = High Risk / Disease Detected (Action needed)
- **Risk Percentage** (0-100%)
- **Current Status Text** (Healthy / At Risk / Critical)

#### **Real-time Sensors Section**
- 🌡️ **Temperature Display**
  - Current value (°C)
  - Graph showing last 24 hours
  - Min/Max indicators
  
- 💧 **Humidity Display**
  - Current value (%)
  - Graph showing last 24 hours
  - Optimal range indicator

- 🌱 **Soil Moisture Display**
  - Current value (%)
  - Gauge visualization
  - Dry/Wet indicator

#### **Quick Action Buttons**
- 📷 **Scan Leaf Now** → Go to Scan Screen
- 📊 **View History** → Go to History Screen
- ⚠️ **View Alerts** → Go to Alerts Screen
- ⚙️ **Settings** → Go to Settings Screen

#### **Recent Alerts Section** (Last 5)
- 🔴 Alert Icon
- Alert Title (e.g., "Disease Detected in Zone A1")
- Alert Time
- Alert Type Badge (disease/warning/info)
- Swipe → Full Alert Details

#### **Bottom Navigation Bar**
- 🏠 Dashboard (Current)
- 📷 Scan
- 📊 History
- ⚠️ Alerts
- ⚙️ Settings

**Functionality:**
- Auto-refresh every 10 seconds
- Tap sensor cards to see detailed graphs
- Tap alerts to see full description
- Real-time WebSocket updates (if implemented)
- Offline mode: Show cached data

**Data Flow:**
```
GET /iot/sensors/{farm_id}/latest → Display Temperature/Humidity/Soil
GET /alerts/?limit=5 → Display Recent Alerts
GET /iot/sensors/{farm_id}/risk → Display Risk Level & Status
```

---

### **4. SCAN SCREEN** 📸
**Purpose:** Capture or upload tomato leaf photos for AI disease detection
**User Role Required:** Farmer, Technician
**Sub-Screens:** Camera, Gallery, Analysis Results

**Components:**

#### **Tab 1: Camera Capture**
- 📹 Live Camera Preview
- 🔵 Capture Button (Red Circle in center)
- 🔄 Flip Camera (Front/Back)
- 🔦 Flash Toggle (On/Off/Auto)
- 📷 Gallery Access Button
- ⏱️ Countdown Timer (3-5 seconds before auto-analysis)
- 📍 Zone Selection Dropdown (A1, B2, etc.)

#### **Tab 2: Upload from Gallery**
- 🖼️ Gallery Thumbnail Grid
- ✅ Select Image
- ⏱️ 3-second countdown before auto-analysis
- 📍 Zone Selection

#### **Analysis Screen** (After Image Selected)
- 🖼️ Large Image Preview
- ⏳ "Analyzing..." Loading Spinner (3-5 seconds)
- 📊 Analysis Progress Bar

#### **Results Screen** (After Analysis Complete)
- 🖼️ Selected Leaf Image
- 🦠 **Disease Detection Result**
  - Disease Name (e.g., "Early Blight")
  - Confidence Score (0-100%)
  - Severity Badge (Low/Medium/High/Critical)
  
- 📖 **Disease Description**
  - What is this disease?
  - How does it spread?
  
- 💊 **Treatment Recommendation**
  - Recommended actions
  - Fungicide suggestions
  - Prevention tips
  
- 📍 **Zone Information**
  - Affected Zone Code (A1, B2, etc.)
  - Zone Health Status
  
- 🔘 **Action Buttons**
  - ✅ Save Detection
  - 📸 Scan Another Leaf
  - 📊 View Zone History
  - 📤 Share Result

**Functionality:**
- Auto-focus on leaf area
- Auto-brightness adjustment
- Compresses image before upload (max 5MB)
- Sends multipart request to /disease/predict
- Shows 3-5 second countdown before analyzing
- Automatically triggers analysis after countdown
- Displays confidence level with visual indicator
- Saves detection to database
- Creates alert for farmer if disease detected

**Data Flow:**
```
Capture/Select Image → Compress → Wait 3-5 seconds → HTTP POST /disease/predict 
→ Get AI Result → Display: Disease Name + Confidence + Treatment → Save Detection
```

---

### **5. HISTORY SCREEN** 📈
**Purpose:** View past scans, detections, and sensor readings
**User Role Required:** Farmer, Technician
**Access:** View their own farm data only

**Components:**

#### **Tab 1: Disease Detections History**
- 📅 Date Filter (Last 7 days, 30 days, All)
- 🔍 Search by Disease Name
- 📊 Sort Options (Newest, Oldest, High Confidence)

**Detection List Items:**
- 🖼️ Thumbnail of scanned leaf
- 🦠 Disease Name
- 📊 Confidence Score (%)
- 📍 Zone Code where detected
- 📅 Detection Date & Time
- 🏷️ Status Badge (Active/Treated/Resolved)
- ➡️ Tap → View Full Details

**Detection Details (Tap Item):**
- Large leaf image
- Full disease information
- Treatment history (if treated)
- Recommendation status
- Update status button (Mark as Treated/Resolved)

#### **Tab 2: Sensor Readings History**
- 📅 Date Range Selector
- 📊 Multiple Graph Options:
  - Temperature over time
  - Humidity over time
  - Soil Moisture over time
  - Risk Level trend

**Graph Features:**
- 📉 Interactive line/area charts
- 🔍 Zoom and pan capability
- 📍 Touch point to see exact values
- 🎨 Color-coded (Safe/Warning/Critical)
- 📥 Download as CSV option

#### **Tab 3: Alerts History**
- 📅 Date Filter
- 🏷️ Alert Type Filter (Disease/Warning/Info)
- 📋 Alert List (Newest first)

**Alert Items:**
- ⏰ Alert Time
- 📌 Alert Title
- 🔴 Severity Badge (Low/Medium/High/Critical)
- 📖 Alert Message
- ✅ Read/Unread Status

**Functionality:**
- Load data from GET /disease/{farm_id}/detections
- Load sensor data from GET /iot/sensors/{farm_id}/history
- Load alerts from GET /alerts/farm/{farm_id}
- Charts update in real-time
- Pagination for large datasets (20 items per page)
- Export functionality to CSV

**Data Flow:**
```
GET /disease/{farm_id}/detections → Display Disease History
GET /iot/sensors/{farm_id}/history → Display Sensor Charts
GET /alerts/farm/{farm_id} → Display Alert History
```

---

### **6. ALERTS SCREEN** 🚨
**Purpose:** View active alerts and notifications
**User Role Required:** Farmer, Technician
**Access:** View their farm's alerts only

**Components:**

#### **Alert Summary Section**
- 🔴 Total Active Alerts (count)
- 🟠 High Risk Count
- 🟡 Medium Risk Count
- 🟢 Low Risk Count

#### **Filter Bar**
- 🏷️ Filter by Type (All, Disease, Warning, Info)
- 🎯 Filter by Status (Active, Resolved)
- 📅 Filter by Date (Today, This Week, All)

#### **Active Alerts List**
Each alert shows:
- 🔴 Severity Icon (Red/Orange/Yellow/Green)
- 📌 Alert Title
- 📖 Brief Description
- ⏰ Time Ago (e.g., "2 hours ago")
- 📍 Zone Code (if location-specific)
- ➡️ Expand arrow

**Expanded Alert Details:**
- Full alert message
- Affected zone map (if applicable)
- Related detection (if disease alert)
- 📊 Recommended actions
- ✅ Mark as Read Button
- ❌ Dismiss Button
- 🔗 "View Details" → Go to related detection

#### **No Alerts State**
- 🟢 Checkmark Icon
- "No Active Alerts"
- "Your farm is healthy!"
- Refresh button

**Functionality:**
- Load alerts from GET /alerts/farm/{farm_id}
- Auto-refresh every 30 seconds
- Push notifications for new alerts
- Mark alerts as read
- Sound notification for critical alerts (if enabled)
- Auto-dismiss after 24 hours (configurable)

**Data Flow:**
```
GET /alerts/farm/{farm_id} → Filter & Sort → Display Alerts
PATCH /alerts/{alert_id}/read → Mark as Read
DELETE /alerts/{alert_id} → Dismiss Alert
```

---

### **7. SETTINGS SCREEN** ⚙️
**Purpose:** Configure app preferences, profile, and notifications
**User Role Required:** Authenticated User

**Components:**

#### **Profile Section** 👤
- 👥 User Avatar (Editable)
- 📝 Full Name (Editable)
- 📧 Email (Read-only, for display)
- 📱 Phone Number (Editable)
- 🎯 Role Badge (Farmer/Technician - Read-only)
- ✏️ Edit Profile Button

#### **Notifications Settings** 🔔
- 🔕 Enable/Disable All Notifications (Toggle)
- 🦠 Disease Alerts (Toggle)
- ⚠️ Risk Warnings (Toggle)
- 📊 Sensor Updates (Toggle)
- 🔊 Sound Notifications (Toggle)
- 📳 Vibration (Toggle)
- 🔉 Notification Volume Slider

#### **Farm Settings** 🌾
- 🌾 Default Farm Selection (Dropdown)
- 📍 Default Zone (Dropdown)
- 📏 Farm Size (Text input)
- 🗺️ Farm Location (Map picker)
- 🥬 Crop Type (Tomato - Fixed/Read-only)

#### **App Preferences** 📱
- 🌙 Dark Mode (Toggle)
- 🌐 Language Selection (English/French/Kinyarwanda)
- 📏 Units (Celsius/Fahrenheit, %)
- ⏱️ Auto-refresh Interval (5s, 10s, 30s, 1min)

#### **Privacy & Security** 🔐
- 🔐 Change Password Button → Modal Form
- 🗑️ Delete Account Button → Confirmation Dialog
- 📜 Privacy Policy Link (Web view)
- ⚖️ Terms of Service Link (Web view)

#### **App Information** ℹ️
- 📦 App Version
- 🔗 Website Link
- 📧 Support Email
- 🐛 Report Bug Link

#### **Logout Section** 🚪
- 🚪 **Logout Button** (Red/Danger color)
- Confirmation dialog before logout

**Functionality:**
- Save preferences to local device storage
- Sync profile changes with backend (PUT /auth/profile)
- Change password (PUT /auth/change-password)
- Delete account with confirmation
- Update notification preferences locally

---

## 🖥️ DASHBOARD (WEB) OVERVIEW

**Platform:** Next.js/React (Web browser)
**Purpose:** Farm management, analytics, and system monitoring
**Users:** Farmers, Agricultural Technicians, Farm Managers, Admin

---

## 👥 USER ROLES & ACCESS CONTROL

### **1. FARMER** 🌾
**Who:** Individual farmer or farm owner
**Access Level:** Personal farm data only

**Permissions:**
- ✅ View own farm dashboard
- ✅ Scan leaves on own farm
- ✅ View own detections & alerts
- ✅ View own sensor data
- ✅ Manage own profile
- ❌ Cannot access other farms
- ❌ Cannot access admin panel
- ❌ Cannot manage users

**Dashboard Pages Accessible:**
- Dashboard (own farm only)
- Scan
- History
- Alerts
- Settings

---

### **2. TECHNICIAN** 🔧
**Who:** Agricultural technician assigned to farm
**Access Level:** Assigned farms only

**Permissions:**
- ✅ View assigned farm dashboards
- ✅ Scan leaves on assigned farms
- ✅ View detections & alerts for assigned farms
- ✅ Record treatment actions
- ✅ Generate reports
- ✅ Manage assigned zones
- ❌ Cannot access unassigned farms
- ❌ Cannot access admin panel
- ❌ Cannot manage users

**Dashboard Pages Accessible:**
- Dashboard (assigned farms)
- Scan (assigned farms)
- History (assigned farms)
- Alerts (assigned farms)
- Reports
- Settings

---

### **3. FARM MANAGER** 👨‍💼
**Who:** Farm owner managing multiple farms
**Access Level:** All farms in their organization

**Permissions:**
- ✅ View all organization farms
- ✅ Manage farm zones
- ✅ Assign technicians to farms
- ✅ View comprehensive analytics
- ✅ Generate reports
- ✅ Manage farm settings
- ✅ Invite technicians
- ❌ Cannot access system admin functions
- ❌ Cannot manage user roles

**Dashboard Pages Accessible:**
- Dashboard (all farms)
- Zones Management
- Team Management
- Analytics & Reports
- Settings

---

### **4. ADMIN** 🔐
**Who:** System administrator
**Access Level:** Entire system

**Permissions:**
- ✅ View all users
- ✅ View all farms
- ✅ View all detections
- ✅ Manage user roles & permissions
- ✅ Deactivate users
- ✅ Manage disease database
- ✅ Access system logs
- ✅ Manage API tokens
- ✅ View system analytics
- ✅ Export all data

**Dashboard Pages Accessible:**
- Dashboard (system overview)
- User Management
- Farm Management
- Disease Database
- System Logs
- Analytics
- Settings (system-wide)

---

## 🖥️ WEB DASHBOARD - PAGES & COMPONENTS

### **1. DASHBOARD PAGE** 📊
**Accessible By:** All authenticated users (role-based data)
**Purpose:** Overview of farm health and key metrics

**Components:**

#### **Header Section**
- 🏢 Company Logo
- 🍅 "TomatoGuard" Title
- 🌾 Farm/Organization Selector (Dropdown)
- 🔔 Notification Bell
- 👤 User Profile Menu
- 🚪 Logout Button

#### **Main Dashboard Grid**

**1. Summary Cards (Row 1)**
- 🟢 **Healthy Zones** Card
  - Number of disease-free zones
  - Trend indicator (↑ or ↓)
  - Percentage of total zones
  
- 🔴 **Affected Zones** Card
  - Number of zones with detected disease
  - Trend indicator
  - Most common disease
  
- ⚠️ **Active Alerts** Card
  - Count of unresolved alerts
  - High/Medium/Low breakdown
  - "View All" link

- 🌡️ **Average Conditions** Card
  - Avg Temperature
  - Avg Humidity
  - Avg Soil Moisture

**2. Zone Health Map (Row 2)**
- 🗺️ Farm Zone Grid (A1-D4, 16 zones)
- 🟢 Green = Healthy
- 🟡 Yellow = Medium Risk
- 🔴 Red = High Risk / Disease Detected
- Click zone → Zone Details Page
- Last update timestamp

**3. Real-time Sensor Data (Row 3)**
- 📈 **Temperature Graph**
  - 24-hour line chart
  - Current value
  - Min/Max
  - Target range shaded

- 📈 **Humidity Graph**
  - 24-hour line chart
  - Current value
  - Optimal range shaded
  - Deviation alerts

- 📈 **Soil Moisture Graph**
  - 24-hour line chart
  - Current value
  - Dry/Wet indicators
  - Irrigation recommendations

**4. Recent Detections (Row 4)**
- 📋 Table format:
  - Date | Leaf Image | Disease | Confidence | Zone | Status
- Sortable by date/disease
- Clickable rows → Detection Details
- Show 10 items, pagination for more

**5. Active Alerts (Row 5)**
- 🚨 Alert List
- 🔴 Color-coded by severity
- Time-based organization (Recent first)
- "View All Alerts" link

**Functionality:**
- Real-time data refresh (every 10 seconds)
- Responsive design (mobile/tablet/desktop)
- Exportable dashboard as PDF
- Customizable widgets (add/remove/resize)

---

### **2. ZONES MANAGEMENT PAGE** 🗺️
**Accessible By:** Farm Manager, Technician, Admin
**Purpose:** View and manage individual farm zones

**Components:**

#### **Zone Grid View**
- 16 zones displayed (A1-D4)
- Each zone shows:
  - Zone Code (A1, A2, etc.)
  - Health Status (Color)
  - Last Reading Time
  - Current Risk Level
  - Disease Count (if any)
  
- Click zone → Zone Details

#### **Zone Details Modal/Page**
- 📍 Zone Code
- 📊 Health Status (Large indicator)
- 🌡️ Last Temperature
- 💧 Last Humidity
- 🌱 Last Soil Moisture
- 🦠 Diseases Detected (If any)
- 📈 24-hour sensor graphs
- 📋 Recent detections in this zone
- ⚠️ Active alerts for this zone
- 🔧 Assign Technician (Farm Manager only)
- 📝 Zone Notes/Comments
- 📍 Zone GPS Coordinates

**Functionality:**
- Bulk actions (Select multiple zones)
- Assign technicians to zones
- Add custom notes
- View zone-specific history
- Export zone data

---

### **3. DISEASE DETECTION PAGE** 🦠
**Accessible By:** Farmer, Technician, Farm Manager, Admin
**Purpose:** View all disease detections with filtering and analysis

**Components:**

#### **Filter Bar**
- 🔍 Search by Disease Name
- 📅 Date Range Picker (From - To)
- 🎯 Filter by Zone (Multi-select)
- 📊 Filter by Severity (Low/Medium/High/Critical)
- 🏷️ Filter by Status (Active/Treated/Resolved)

#### **Detection Table**
- Columns: Date | Image | Disease | Confidence | Severity | Zone | Status | Actions
- 📊 Sortable by any column
- Clickable rows → Full Detection Details
- 🎨 Row colors based on severity (Red/Orange/Yellow/Green)

#### **Detection Details View**
- 🖼️ Full leaf image
- 📊 Disease Information:
  - Name
  - Confidence Score (%)
  - Severity Level
  - Description
  - Characteristics
  
- 💊 Treatment Recommendation:
  - Suggested treatment
  - Fungicide options
  - Prevention tips
  - Expected recovery time
  
- 📊 Zone & Farm Info:
  - Farm name
  - Zone code
  - Farmer name
  
- 📝 Status Management:
  - Current status (Active/Treated/Resolved)
  - Change status button
  - Treatment notes
  - Date resolved
  
- 📞 Actions:
  - Notify farmer
  - Generate report
  - Share with technician
  - Delete record

**Functionality:**
- Bulk export to CSV/PDF
- AI confidence filtering
- Detection timeline
- Comparison tool (before/after treatment)
- Farmer notification system

---

### **4. ALERTS PAGE** ⚠️
**Accessible By:** Farmer, Technician, Farm Manager, Admin
**Purpose:** Monitor and manage all alerts

**Components:**

#### **Alert Dashboard**
- 🔴 Total Active Alerts
- 🟠 Critical Alerts
- 🟡 Medium Alerts
- 🟢 Resolved Alerts

#### **Alert Filter & Search**
- 🔍 Search by alert title
- 📅 Date filter
- 🏷️ Alert type filter (Disease/Warning/Info)
- 🎯 Zone filter
- 📊 Severity filter

#### **Alert List**
- Organized by urgency:
  1. 🔴 Critical (Active)
  2. 🟠 High (Active)
  3. 🟡 Medium (Active)
  4. Resolved alerts

**Alert Item Shows:**
- Alert title
- Description
- Zone affected
- Time received
- Severity badge
- Status (Active/Resolved)
- Linked detection (if disease)

#### **Alert Actions**
- ✅ Mark as Read
- ✅ Mark as Resolved
- 📧 Send Notification
- 📞 Call Technician
- 📊 View Details

**Functionality:**
- Real-time alert notifications
- Sound & visual alerts for critical items
- Auto-escalation if not resolved within timeframe
- Bulk mark as read/resolved
- Alert history

---

### **5. ANALYTICS & REPORTS PAGE** 📈
**Accessible By:** Farm Manager, Admin, Technician
**Purpose:** View trends and generate reports

**Components:**

#### **Time Period Selector**
- 📅 Custom date range
- Quick options: Last 7 days, 30 days, 90 days, 1 year

#### **Dashboard Analytics**

**1. Disease Statistics**
- 📊 Pie chart: Disease distribution
- Most common diseases
- Trend over time
- Seasonal patterns

**2. Detection Trends**
- 📈 Line chart: Detections per day
- 🎯 Zone comparison
- Early vs Late detection
- Recovery rate

**3. Risk Analysis**
- 🌡️ Temperature vs Disease correlation
- 💧 Humidity vs Disease correlation
- 🌱 Soil Moisture impact
- Risk level distribution

**4. Zone Performance**
- 📊 Comparison chart
- Best performing zone
- Worst performing zone
- Trend indicators

**5. Treatment Effectiveness**
- 📊 Treated vs Resolved count
- Average treatment duration
- Most effective treatments
- Recovery success rate

#### **Report Generation**
- 📄 Generate PDF Report
- 📊 Generate Excel Report
- 📧 Schedule email reports
- 🔗 Share report link
- 📝 Custom report builder

**Report Includes:**
- Executive summary
- Disease statistics
- Zone analysis
- Treatment recommendations
- Risk assessment
- Trend analysis
- Farmer recommendations

**Functionality:**
- Interactive charts (zoom, filter, drill-down)
- Export to multiple formats
- Scheduled automated reports
- Comparison tools (zone vs zone, period vs period)
- Predictive analytics (disease forecast)

---

### **6. TEAM MANAGEMENT PAGE** 👥
**Accessible By:** Farm Manager, Admin
**Purpose:** Manage technicians and farm access

**Components:**

#### **User List**
- Table: Name | Email | Role | Farm(s) | Status | Actions
- 📊 Sortable & filterable

#### **User Details View**
- 👤 Avatar
- 📝 Full Name
- 📧 Email
- 📱 Phone
- 🎯 Role (Farmer/Technician/Manager/Admin)
- 🌾 Assigned Farms (Multi-select)
- 📍 Assigned Zones
- ✅ Active/Inactive Status
- 📅 Join Date
- 🔧 Action buttons:
  - Edit
  - Change Role
  - Reset Password
  - Deactivate/Activate
  - Delete

#### **Invite New Technician**
- 📧 Email input
- 🎯 Select role
- 🌾 Assign farms
- 📝 Invitation message
- 📤 Send Invite

**Functionality:**
- Bulk user management
- Permission templates
- Activity logs per user
- Access audit trail

---

### **7. SETTINGS PAGE** ⚙️
**Accessible By:** All users (personal) + Admin (system-wide)

**Components:**

#### **Personal Settings** (All Users)
- 👤 Profile Information
  - Full Name
  - Email
  - Phone
  - Profile Picture
  
- 🔐 Security
  - Change Password
  - Two-Factor Authentication (if enabled)
  - Login History
  
- 🔔 Notification Preferences
  - Email notifications
  - Push notifications
  - Alert types
  - Frequency

#### **Farm Settings** (Farm Manager)
- 🌾 Farm Information
  - Farm name
  - Location
  - Total area
  - Crop type (Tomato)
  
- 🌾 Zone Management
  - Create/Edit zones
  - Zone coordinates
  - Zone assignments

#### **System Settings** (Admin Only)
- 🔧 API Configuration
- 🗄️ Database Management
- 🔐 Security Settings
- 🌐 Email Configuration
- 📊 System Logs
- 💾 Backup & Restore

---

## 🔄 DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    ESP32-CAM IoT Device                      │
├─────────────────────────────────────────────────────────────┤
│  • DHT11 Sensor (Temp/Humidity)                              │
│  • Soil Moisture Sensor                                      │
│  • Camera (Leaf photos)                                      │
│  • LED Indicators (Status)                                   │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─ POST /iot/sensors (every 10 seconds)
             │  └─ {farm_id, temp, humidity, soil_moisture}
             │
             └─ POST /disease/predict (every 60 seconds)
                └─ {file: image, farm_id, zone_code}

                            ↓

         ┌──────────────────────────────────┐
         │     FastAPI Backend Server       │
         ├──────────────────────────────────┤
         │  • Receives sensor data          │
         │  • Runs AI disease detection     │
         │  • Stores in Supabase            │
         │  • Creates alerts                │
         │  • Manages users                 │
         └───────────────┬──────────────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
     POST /iot/sensors   POST /      GET /alerts
     stored in DB    /disease/        (mobile &
                    predict          dashboard)
            │            │            │
            ↓            ↓            ↓
     ┌─────────────────────────────────┐
     │    Supabase PostgreSQL DB       │
     ├─────────────────────────────────┤
     │ • sensor_logs                   │
     │ • detections                    │
     │ • alerts                        │
     │ • users                         │
     │ • farms                         │
     │ • zones                         │
     └────────┬────────────────────────┘
              │
   ┌──────────┴──────────┐
   │                     │
   ↓                     ↓
┌─────────────┐      ┌──────────────┐
│  Flutter    │      │ Next.js      │
│  Mobile App │      │ Web Dashboard│
├─────────────┤      ├──────────────┤
│ • Dashboard │      │ • Dashboard  │
│ • Scan      │      │ • Analytics  │
│ • History   │      │ • Team Mgmt  │
│ • Alerts    │      │ • Reports    │
│ • Settings  │      │ • Settings   │
└─────────────┘      └──────────────┘
```

---

## 📋 COMPONENT CHECKLIST BY PAGE

### **Mobile App**
- [ ] Login Screen
- [ ] Register Screen
- [ ] Dashboard Screen (home)
- [ ] Scan Screen (camera + analysis)
- [ ] History Screen (charts + records)
- [ ] Alerts Screen
- [ ] Settings Screen
- [ ] Navigation Bar (5 tabs)

### **Web Dashboard**
- [ ] Dashboard Page (overview)
- [ ] Zones Management Page
- [ ] Disease Detection Page
- [ ] Alerts Page
- [ ] Analytics & Reports Page
- [ ] Team Management Page
- [ ] Settings Page
- [ ] User Authentication
- [ ] Header/Navigation

---

## 🔐 AUTHENTICATION FLOW

```
┌─────────────────────────────────┐
│  User enters email + password    │
└────────────┬────────────────────┘
             │
             ↓
  POST /auth/login (Mobile/Web)
             │
             ├─ Validate credentials
             │
             ├─ Generate JWT token
             │
             ├─ Return token + user info
             │
             ↓
  ┌─────────────────────────────┐
  │ Store token in device/browser│
  │ (localStorage / shared prefs) │
  └────────────┬────────────────┘
               │
               ↓
    Use token in all API requests:
    Authorization: Bearer {token}
               │
               ├─ If valid → Process request
               │
               └─ If expired → Refresh token
                              or redirect to login
```

---

## 📱 RESPONSIVE DESIGN

### **Mobile (< 640px)**
- Full-width single column
- Bottom navigation bar
- Touch-optimized buttons
- Vertical scrolling
- Simplified charts

### **Tablet (640px - 1024px)**
- Two-column layout
- Side navigation drawer
- Medium charts
- Optimized for touch & keyboard

### **Desktop (> 1024px)**
- Three-column layout
- Side navigation menu
- Interactive data visualizations
- Keyboard shortcuts
- Multi-window support

---

## 🎯 KEY METRICS DISPLAYED

**For Farmers:**
- Farm health status
- Recent detections
- Active alerts
- Current sensor readings
- Treatment recommendations

**For Technicians:**
- Assigned farm dashboard
- Zone-specific data
- Treatment history
- Report generation
- Team communication

**For Farm Managers:**
- Multi-farm overview
- Comparative analytics
- Team performance
- Budget/cost analysis
- Trend forecasting

**For Admin:**
- System-wide analytics
- User management
- Database health
- API usage
- System logs

---

## 🚀 DEPLOYMENT

**Mobile:**
- iOS: App Store
- Android: Google Play Store

**Web:**
- Hosted on cloud (AWS, Vercel, or similar)
- Accessible at: www.tomato-guard.rw (example domain)

**Backend:**
- FastAPI server on cloud
- Supabase PostgreSQL database
- Ngrok for local development

---

**Version:** 1.0
**Last Updated:** June 2026
**Status:** In Development
