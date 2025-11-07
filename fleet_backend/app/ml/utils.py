"""ML utility functions for predictions."""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from app.ml.loader import ml_models


def prepare_sensor_data_for_prediction(sensor_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert sensor data dictionary to DataFrame suitable for ML models.
    
    Args:
        sensor_data: Dictionary containing sensor readings
        
    Returns:
        DataFrame with features in correct order
    """
    # Expected features for the model (adjust based on your training data)
    features = {
        'speed': sensor_data.get('speed', 0.0),
        'battery': sensor_data.get('battery', 100.0),
        'acc_x': sensor_data.get('acc_x', 0.0),
        'acc_y': sensor_data.get('acc_y', 0.0),
        'acc_z': sensor_data.get('acc_z', 0.0),
        'temp_motor': sensor_data.get('temp_motor', 25.0),
    }
    
    # Create DataFrame
    df = pd.DataFrame([features])
    return df


def run_failure_prediction(sensor_data: Dict[str, Any]) -> Tuple[int, float]:
    """
    Run failure prediction using Random Forest and Logistic Regression.
    
    Args:
        sensor_data: Dictionary containing sensor readings
        
    Returns:
        Tuple of (failure_prediction, confidence)
    """
    try:
        # Get models
        rf_model = ml_models.get_rf_model()
        lr_model = ml_models.get_lr_model()
        
        if not rf_model or not lr_model:
            print("⚠ Models not loaded, returning default prediction")
            return 0, 0.5
        
        # Prepare data
        df = prepare_sensor_data_for_prediction(sensor_data)
        
        # Get predictions
        rf_pred = rf_model.predict(df)[0]
        
        # Get probability from LR model
        try:
            lr_proba = lr_model.predict_proba(df)[0]
            confidence = float(lr_proba[1] if rf_pred == 1 else lr_proba[0])
        except:
            # If predict_proba not available, use decision function or default
            confidence = 0.75 if rf_pred == 1 else 0.25
        
        return int(rf_pred), confidence
        
    except Exception as e:
        print(f"Error in failure prediction: {e}")
        return 0, 0.5


def run_anomaly_detection(sensor_data: Dict[str, Any]) -> Tuple[int, float]:
    """
    Run anomaly detection using Isolation Forest.
    
    Args:
        sensor_data: Dictionary containing sensor readings
        
    Returns:
        Tuple of (anomaly_flag, iso_score)
    """
    try:
        # Get model
        iso_model = ml_models.get_iso_model()
        
        if not iso_model:
            print("⚠ Isolation Forest model not loaded, returning default")
            return 0, 0.0
        
        # Prepare data
        df = prepare_sensor_data_for_prediction(sensor_data)
        
        # Get prediction (-1 for anomaly, 1 for normal)
        iso_pred = iso_model.predict(df)[0]
        
        # Get anomaly score
        try:
            iso_score = iso_model.score_samples(df)[0]
        except:
            iso_score = -0.5 if iso_pred == -1 else 0.5
        
        # Convert to flag (1 if anomaly, 0 if normal)
        anomaly_flag = 1 if iso_pred == -1 else 0
        
        return int(anomaly_flag), float(iso_score)
        
    except Exception as e:
        print(f"Error in anomaly detection: {e}")
        return 0, 0.0


def generate_prediction_message(
    failure_pred: int,
    confidence: float,
    anomaly_flag: int,
    iso_score: float
) -> str:
    """
    Generate human-readable message based on predictions.
    
    Args:
        failure_pred: Failure prediction (0 or 1)
        confidence: Confidence score
        anomaly_flag: Anomaly flag (0 or 1)
        iso_score: Isolation forest score
        
    Returns:
        Message string
    """
    if failure_pred == 1 and confidence > 0.7:
        if anomaly_flag == 1:
            return "Critical: High risk of motor failure with anomalous behavior detected"
        return "High risk of motor failure detected"
    elif failure_pred == 1:
        return "Moderate risk of failure detected, monitoring recommended"
    elif anomaly_flag == 1:
        return "Anomalous sensor readings detected, inspection recommended"
    else:
        return "Vehicle operating normally"


def predict_all(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run all predictions on sensor data.
    
    Args:
        sensor_data: Dictionary containing sensor readings
        
    Returns:
        Dictionary with all prediction results
    """
    # Run failure prediction
    failure_pred, confidence = run_failure_prediction(sensor_data)
    
    # Run anomaly detection
    anomaly_flag, iso_score = run_anomaly_detection(sensor_data)
    
    # Generate message
    message = generate_prediction_message(failure_pred, confidence, anomaly_flag, iso_score)
    
    return {
        "failure": failure_pred,
        "confidence": confidence,
        "anomaly": bool(anomaly_flag),
        "anomaly_flag": anomaly_flag,
        "iso_score": iso_score,
        "message": message
    }
