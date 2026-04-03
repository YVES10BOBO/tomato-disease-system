def calculate_risk(temperature: float, humidity: float, soil_moisture: float) -> dict:
    """
    Calculate disease risk level based on sensor readings.
    Returns risk level and list of diseases likely to occur.
    """
    risks = []
    risk_level = "low"

    # Late Blight: temp 10-25°C + humidity > 90%
    if 10 <= temperature <= 25 and humidity >= 90:
        risks.append({
            "disease": "Late Blight",
            "probability": "critical",
            "action": "Apply metalaxyl fungicide immediately. Inspect all zones."
        })
        risk_level = "critical"

    # Early Blight: temp 24-29°C + humidity > 80%
    elif 24 <= temperature <= 29 and humidity >= 80:
        risks.append({
            "disease": "Early Blight",
            "probability": "high",
            "action": "Apply copper-based fungicide. Check lower leaves."
        })
        risk_level = "high"

    # Bacterial Wilt: temp 25-35°C + high soil moisture
    if 25 <= temperature <= 35 and soil_moisture >= 80:
        risks.append({
            "disease": "Bacterial Wilt",
            "probability": "high",
            "action": "Reduce irrigation immediately. Improve drainage."
        })
        if risk_level == "low":
            risk_level = "high"

    # Septoria Leaf Spot: temp 20-25°C + humidity > 70%
    if 20 <= temperature <= 25 and humidity >= 70:
        risks.append({
            "disease": "Septoria Leaf Spot",
            "probability": "medium",
            "action": "Apply chlorothalonil fungicide. Avoid wetting leaves."
        })
        if risk_level == "low":
            risk_level = "medium"

    # Leaf Curl Virus: temp > 30°C + low humidity (spread by whiteflies)
    if temperature > 30 and humidity < 50:
        risks.append({
            "disease": "Leaf Curl Virus",
            "probability": "medium",
            "action": "Control whitefly population. Apply insecticide."
        })
        if risk_level == "low":
            risk_level = "medium"

    # General warning: humidity > 85%
    if humidity >= 85 and risk_level == "low":
        risk_level = "medium"

    return {
        "risk_level": risk_level,
        "risks": risks,
        "summary": _get_summary(risk_level, temperature, humidity, soil_moisture)
    }


def _get_summary(risk_level: str, temp: float, humidity: float, soil: float) -> str:
    if risk_level == "critical":
        return f"CRITICAL: Conditions extremely favorable for disease. Temp {temp}°C, Humidity {humidity}%. Act immediately."
    elif risk_level == "high":
        return f"HIGH RISK: Disease conditions detected. Temp {temp}°C, Humidity {humidity}%. Apply treatment soon."
    elif risk_level == "medium":
        return f"MODERATE RISK: Monitor closely. Temp {temp}°C, Humidity {humidity}%. Consider preventive measures."
    else:
        return f"Farm conditions normal. Temp {temp}°C, Humidity {humidity}%, Soil moisture {soil}%."
