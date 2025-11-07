"""Mock sensor script for testing Fleet Management System.

This script simulates a vehicle sending real-time sensor data to the backend API.
It continuously sends random sensor readings every second.
"""
import requests
import time
import random
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
SENSOR_DATA_ENDPOINT = f"{API_BASE_URL}/sensor-data"
VEHICLE_ID = 1  # Change this to test different vehicles
SEND_INTERVAL = 1  # seconds


def generate_random_sensor_data(vehicle_id: int) -> dict:
    """
    Generate random sensor data mimicking a real vehicle.
    
    Args:
        vehicle_id: ID of the vehicle
        
    Returns:
        Dictionary with sensor readings
    """
    # Generate realistic sensor values
    sensor_data = {
        "vehicle_id": 1,
        "gps_lat": round(random.uniform(37.0, 38.0), 6),  # San Francisco area
        "gps_lon": round(random.uniform(-122.5, -122.0), 6),
        "speed": round(random.uniform(0, 80), 2),  # 0-80 km/h
        "battery": round(random.uniform(20, 100), 2),  # 20-100%
        "acc_x": round(random.uniform(-2, 2), 3),  # -2 to 2 m/s²
        "acc_y": round(random.uniform(-2, 2), 3),
        "acc_z": round(random.uniform(-2, 2), 3),
        "temp_motor": round(random.uniform(20, 90), 2),  # 20-90°C
        "raw_payload": {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_version": "v2.1.0",
            "location": "highway_101"
        }
    }
    
    # Occasionally simulate anomalies (5% chance)
    if random.random() < 0.05:
        sensor_data["temp_motor"] = round(random.uniform(95, 120), 2)  # High temp
        sensor_data["battery"] = round(random.uniform(5, 15), 2)  # Low battery
        print("Simulating anomaly conditions...")
    
    return sensor_data


def send_sensor_data(sensor_data: dict) -> None:
    """
    Send sensor data to the API endpoint.
    
    Args:
        sensor_data: Sensor data dictionary
    """
    try:
        response = requests.post(
            SENSOR_DATA_ENDPOINT,
            json=sensor_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✓ Data sent successfully!")
            print(f"  Vehicle ID: {result['vehicle_id']}")
            print(f"  Sensor Data ID: {result['sensor_data_id']}")
            print(f"  Prediction ID: {result['prediction_id']}")
            print(f"  Failure Prediction: {result['failure']} (confidence: {result['confidence']:.2%})")
            print(f"  Anomaly Detected: {result['anomaly']} (score: {result['iso_score']:.3f})")
            print(f"  Message: {result['message']}")
            
            # Highlight critical conditions
            if result['failure'] == 1 and result['confidence'] > 0.7:
                print(f"\n  CRITICAL: High failure risk detected!")
            elif result['anomaly']:
                print(f"\n  WARNING: Anomalous behavior detected!")

        else:
            print(f"\n✗ Error: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection Error: Cannot connect to API server")
        print(f"  Make sure the server is running at {API_BASE_URL}")
    except requests.exceptions.Timeout:
        print("\n✗ Timeout Error: Request took too long")
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")


def main():
    """Main function to run the mock sensor."""
    print("=" * 70)
    print("🚗 Mock Sensor Script - Fleet Management System")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  API URL: {API_BASE_URL}")
    print(f"  Vehicle ID: {VEHICLE_ID}")
    print(f"  Send Interval: {SEND_INTERVAL} second(s)")
    print(f"\n" + "=" * 70)
    print("Starting sensor data transmission... (Press Ctrl+C to stop)\n")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"Transmission #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")
            
            # Generate and send sensor data
            sensor_data = generate_random_sensor_data(VEHICLE_ID)
            
            # Display what we're sending
            print(f"\nSending sensor data:")
            print(f"  Speed: {sensor_data['speed']} km/h")
            print(f"  Battery: {sensor_data['battery']}%")
            print(f"  Motor Temp: {sensor_data['temp_motor']}°C")
            print(f"  GPS: ({sensor_data['gps_lat']}, {sensor_data['gps_lon']})")
            print(f"  Acceleration: x={sensor_data['acc_x']}, y={sensor_data['acc_y']}, z={sensor_data['acc_z']}")
            
            # Send to API
            send_sensor_data(sensor_data)
            
            # Wait before next transmission
            time.sleep(SEND_INTERVAL)
            
    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print("🛑 Mock sensor stopped by user")
        print(f"Total transmissions: {iteration}")
        print(f"{'='*70}\n")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")


if __name__ == "__main__":
    main()
