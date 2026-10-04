def calculate_risk(temperature: float, humidity: float, soil_moisture: float) -> dict:
    """
    Calculate disease risk level based on sensor readings.
    Returns risk level, predicted diseases, and farmer recommendations.

    AI-based predictive analysis to help farmers prevent diseases before they occur.
    """
    risks = []
    predicted_diseases = []
    risk_level = "low"
    optimal_conditions = True

    # ═══ LATE BLIGHT ═══ (Most dangerous - cool + very wet)
    # Favored by: 10-25°C, humidity > 90%, wet conditions
    if 10 <= temperature <= 25 and humidity >= 90:
        predicted_diseases.append({
            "disease": "Late Blight",
            "likelihood": "CRITICAL",
            "triggers": [
                f"Temperature: {temperature}°C (10-25°C is critical range)",
                f"Humidity: {humidity}% (above 90% is dangerous)"
            ],
            "recommendations": [
                "🚨 URGENT ACTION: Apply metalaxyl fungicide immediately",
                "Inspect all lower leaves and remove infected ones",
                "Reduce watering to minimize leaf wetness",
                "Improve air circulation - prune lower branches",
                "Isolate affected plants from healthy ones",
                "Repeat fungicide every 7-10 days until weather improves"
            ],
            "timeline": "Apply within 24 hours"
        })
        risk_level = "critical"
        optimal_conditions = False

    # ═══ EARLY BLIGHT ═══ (Warm + humid)
    # Favored by: 24-29°C, humidity > 80%
    elif 24 <= temperature <= 29 and humidity >= 80:
        predicted_diseases.append({
            "disease": "Early Blight",
            "likelihood": "HIGH",
            "triggers": [
                f"Temperature: {temperature}°C (warm range favors disease)",
                f"Humidity: {humidity}% (above 80% is risky)"
            ],
            "recommendations": [
                "💊 Apply copper-based fungicide soon",
                "Remove lower leaves (below first flower cluster)",
                "Improve spacing between plants for air circulation",
                "Water at soil level, avoid wetting leaves",
                "Monitor lower leaves daily for brown spots",
                "Apply fungicide every 7-10 days as preventive"
            ],
            "timeline": "Apply within 48 hours"
        })
        risk_level = "high"
        optimal_conditions = False

    # ═══ BACTERIAL SPOT ═══ (Warm + wet)
    # Favored by: 24-30°C + humidity > 80% + high soil moisture
    if 24 <= temperature <= 30 and humidity >= 80:
        predicted_diseases.append({
            "disease": "Bacterial Spot",
            "likelihood": "HIGH",
            "triggers": [
                f"Temperature: {temperature}°C (24-30°C favors bacteria)",
                f"Humidity: {humidity}% (warm and humid)",
                f"Soil moisture: {soil_moisture}% (bacteria thrive in wet conditions)"
            ],
            "recommendations": [
                "🔵 Apply copper-based bactericide",
                "STOP overhead irrigation - use drip irrigation only",
                "Do NOT work with wet plants (spreads bacteria)",
                "Remove infected leaves and burn them",
                "Space plants further apart",
                "Apply bactericide every 10 days in wet conditions"
            ],
            "timeline": "Apply within 48 hours"
        })
        if risk_level == "low":
            risk_level = "high"
        optimal_conditions = False

    # ═══ SEPTORIA LEAF SPOT ═══ (Moderate conditions)
    # Favored by: 20-25°C + humidity > 70%
    if 20 <= temperature <= 25 and humidity >= 70:
        predicted_diseases.append({
            "disease": "Septoria Leaf Spot",
            "likelihood": "MEDIUM",
            "triggers": [
                f"Temperature: {temperature}°C (optimal for fungus)",
                f"Humidity: {humidity}% (above 70% is risky)",
                "Gray/brown spots with black borders on leaves"
            ],
            "recommendations": [
                "⚠️ Apply chlorothalonil fungicide preventively",
                "Remove lower infected leaves",
                "Avoid overhead watering",
                "Increase plant spacing",
                "Monitor middle/upper leaves",
                "Apply fungicide every 7 days as preventive"
            ],
            "timeline": "Apply within 3-5 days"
        })
        if risk_level == "low":
            risk_level = "medium"
        optimal_conditions = False

    # ═══ BACTERIAL WILT ═══ (Hot + waterlogged)
    # Favored by: 28-35°C + soil moisture > 85% (poor drainage)
    if 28 <= temperature <= 35 and soil_moisture >= 85:
        predicted_diseases.append({
            "disease": "Bacterial Wilt",
            "likelihood": "CRITICAL",
            "triggers": [
                f"Temperature: {temperature}°C (hot condition)",
                f"Soil moisture: {soil_moisture}% (waterlogged - poor drainage)",
                "Plants wilt despite wet soil"
            ],
            "recommendations": [
                "🚨 URGENT: Improve drainage immediately",
                "Reduce irrigation - allow soil to dry between waterings",
                "Add mulch to regulate soil moisture",
                "Check for poor drainage - may need field assessment",
                "Remove and destroy wilted plants to prevent spread",
                "Avoid planting in same area next season"
            ],
            "timeline": "Take action immediately"
        })
        if risk_level != "critical":
            risk_level = "critical"
        optimal_conditions = False

    # ═══ LEAF CURL VIRUS ═══ (Hot + dry - whiteflies active)
    # Favored by: > 30°C + humidity < 50% (hot, dry, windy)
    if temperature > 30 and humidity < 50:
        predicted_diseases.append({
            "disease": "Leaf Curl Virus",
            "likelihood": "MEDIUM",
            "triggers": [
                f"Temperature: {temperature}°C (hot - whiteflies active)",
                f"Humidity: {humidity}% (low - whiteflies spread faster)",
                "Leaves curl and yellow - transmitted by whiteflies"
            ],
            "recommendations": [
                "🐛 Control whitefly population",
                "Spray insecticidal soap or neem oil",
                "Use yellow sticky traps to monitor whiteflies",
                "Plant reflective mulch to confuse insects",
                "Avoid excessive nitrogen fertilizer",
                "Remove and destroy heavily infected plants"
            ],
            "timeline": "Apply within 3-5 days"
        })
        if risk_level == "low":
            risk_level = "medium"
        optimal_conditions = False

    # ═══ GENERAL HUMIDITY WARNING ═══
    if humidity >= 85 and risk_level == "low":
        risk_level = "medium"
        optimal_conditions = False

    return {
        "risk_level": risk_level,
        "risks": risks,
        "predicted_diseases": predicted_diseases,
        "optimal_conditions": optimal_conditions,
        "summary": _get_summary(risk_level, temperature, humidity, soil_moisture),
        "current_conditions": {
            "temperature": temperature,
            "humidity": humidity,
            "soil_moisture": soil_moisture
        }
    }


def _get_summary(risk_level: str, temp: float, humidity: float, soil: float) -> str:
    """Generate farmer-friendly summary with actionable guidance"""
    if risk_level == "critical":
        return f"🚨 CRITICAL RISK: Severe disease conditions detected! Temperature {temp}°C, Humidity {humidity}%, Soil {soil}%. TAKE ACTION IMMEDIATELY - Apply fungicide and improve environmental conditions."
    elif risk_level == "high":
        return f"⚠️ HIGH RISK: Favorable disease conditions detected. Temperature {temp}°C, Humidity {humidity}%, Soil {soil}%. Apply treatment within 48 hours to prevent outbreak."
    elif risk_level == "medium":
        return f"⚠️ MODERATE RISK: Monitor closely. Temperature {temp}°C, Humidity {humidity}%, Soil {soil}%. Consider preventive measures - reduce watering, improve air circulation."
    else:
        return f"✅ LOW RISK: Farm conditions are good. Temperature {temp}°C, Humidity {humidity}%, Soil moisture {soil}%. Continue normal monitoring."
