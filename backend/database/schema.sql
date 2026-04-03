-- ============================================
-- TOMATO DISEASE DETECTION SYSTEM
-- Database Schema
-- ============================================


-- 1. USERS TABLE
-- Stores farmers and admin accounts
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'farmer' CHECK (role IN ('farmer', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- 2. FARMS TABLE
-- Each farmer can have one or more farms
CREATE TABLE IF NOT EXISTS farms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    district VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    size_hectares DECIMAL(10, 2),
    total_zones INTEGER DEFAULT 16,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- 3. FARM ZONES TABLE
-- Grid zones per farm (A1, A2, B1, B2 etc.)
CREATE TABLE IF NOT EXISTS farm_zones (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    zone_code VARCHAR(10) NOT NULL,  -- e.g. A1, B3, D4
    row_label VARCHAR(5) NOT NULL,   -- e.g. A, B, C, D
    col_number INTEGER NOT NULL,     -- e.g. 1, 2, 3, 4
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(farm_id, zone_code)
);


-- 4. FARM SETTINGS TABLE
-- Farmer-controlled scan and notification preferences
CREATE TABLE IF NOT EXISTS farm_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    farm_id UUID NOT NULL UNIQUE REFERENCES farms(id) ON DELETE CASCADE,
    scan_interval_minutes INTEGER DEFAULT 30,
    night_mode_start TIME DEFAULT '20:00:00',
    night_mode_end TIME DEFAULT '06:00:00',
    night_scan_interval_minutes INTEGER DEFAULT 60,
    morning_report_time TIME DEFAULT '06:00:00',
    evening_report_time TIME DEFAULT '20:00:00',
    alert_notifications BOOLEAN DEFAULT TRUE,
    warning_notifications BOOLEAN DEFAULT TRUE,
    daily_summary BOOLEAN DEFAULT TRUE,
    risk_sensitivity VARCHAR(10) DEFAULT 'medium' CHECK (risk_sensitivity IN ('low', 'medium', 'high')),
    auto_override_enabled BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- 5. DISEASES TABLE
-- Reference table of known tomato diseases
CREATE TABLE IF NOT EXISTS diseases (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(150),
    description TEXT,
    symptoms TEXT,
    treatment TEXT,
    prevention TEXT,
    severity VARCHAR(10) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    favorable_temp_min DECIMAL(5,2),
    favorable_temp_max DECIMAL(5,2),
    favorable_humidity_min DECIMAL(5,2),
    favorable_humidity_max DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- 6. SENSOR LOGS TABLE
-- IoT sensor readings from ESP32
CREATE TABLE IF NOT EXISTS sensor_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    soil_moisture DECIMAL(5,2),
    risk_level VARCHAR(10) DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- 7. DETECTIONS TABLE
-- AI disease detection results from Raspberry Pi camera
CREATE TABLE IF NOT EXISTS detections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    zone_id UUID REFERENCES farm_zones(id),
    disease_id UUID REFERENCES diseases(id),
    zone_code VARCHAR(10),
    disease_name VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL,
    severity VARCHAR(10) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    image_url TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'treated', 'resolved')),
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);


-- 8. ALERTS TABLE
-- All alerts and notifications sent to farmers
CREATE TABLE IF NOT EXISTS alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    detection_id UUID REFERENCES detections(id),
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('disease', 'warning', 'summary', 'system')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    zone_code VARCHAR(10),
    risk_level VARCHAR(10) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================
-- SEED DATA: Known Tomato Diseases
-- ============================================

INSERT INTO diseases (name, scientific_name, description, symptoms, treatment, prevention, severity, favorable_temp_min, favorable_temp_max, favorable_humidity_min, favorable_humidity_max)
VALUES
(
    'Early Blight',
    'Alternaria solani',
    'Fungal disease causing dark spots on tomato leaves, stems and fruits.',
    'Dark brown spots with concentric rings (target-like), yellowing of surrounding tissue, lower leaves affected first.',
    'Apply copper-based fungicide or mancozeb. Remove and destroy infected leaves. Improve air circulation.',
    'Use disease-free seeds, rotate crops, avoid overhead watering, apply preventive fungicide.',
    'medium',
    24.0, 29.0, 80.0, 100.0
),
(
    'Late Blight',
    'Phytophthora infestans',
    'Highly destructive disease that can destroy entire tomato crops within days.',
    'Water-soaked grey-green spots on leaves, white mold on undersides, dark brown lesions on stems and fruits.',
    'Apply metalaxyl or cymoxanil fungicide immediately. Remove all infected plant parts urgently.',
    'Avoid overhead irrigation, improve drainage, apply preventive fungicide during humid weather.',
    'critical',
    10.0, 25.0, 90.0, 100.0
),
(
    'Leaf Curl Virus',
    'Tomato Yellow Leaf Curl Virus (TYLCV)',
    'Viral disease spread by whiteflies causing severe stunting and yield loss.',
    'Upward curling of leaves, yellowing at leaf margins, stunted plant growth, reduced fruit set.',
    'No cure once infected. Remove infected plants. Control whitefly population with insecticides.',
    'Use virus-resistant varieties, control whiteflies, use reflective mulch, install insect nets.',
    'high',
    28.0, 35.0, 20.0, 60.0
),
(
    'Bacterial Wilt',
    'Ralstonia solanacearum',
    'Soil-borne bacterial disease causing rapid wilting and plant death.',
    'Sudden wilting of entire plant without yellowing, brown discoloration of stem when cut.',
    'No effective chemical cure. Remove and destroy infected plants. Solarize soil.',
    'Use resistant varieties, improve soil drainage, avoid wounding roots, crop rotation.',
    'critical',
    25.0, 35.0, 60.0, 100.0
),
(
    'Septoria Leaf Spot',
    'Septoria lycopersici',
    'Common fungal disease causing numerous small spots on tomato leaves.',
    'Small circular spots with dark borders and light centers, black dots (pycnidia) inside spots, yellowing and leaf drop.',
    'Apply chlorothalonil or copper-based fungicide. Remove affected leaves.',
    'Avoid wetting leaves, use drip irrigation, remove plant debris, crop rotation.',
    'medium',
    20.0, 25.0, 70.0, 100.0
);


-- ============================================
-- INDEXES for better query performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_sensor_logs_farm_id ON sensor_logs(farm_id);
CREATE INDEX IF NOT EXISTS idx_sensor_logs_recorded_at ON sensor_logs(recorded_at);
CREATE INDEX IF NOT EXISTS idx_detections_farm_id ON detections(farm_id);
CREATE INDEX IF NOT EXISTS idx_detections_detected_at ON detections(detected_at);
CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_farm_id ON alerts(farm_id);
CREATE INDEX IF NOT EXISTS idx_alerts_is_read ON alerts(is_read);
