"""
Test script to verify the Fleet Management System is working correctly.
Run this after starting the backend server.
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_health_check():
    """Test 1: Health check endpoint."""
    print_section("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Server is healthy")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error connecting to server: {e}")
        print(f"  Make sure server is running at {BASE_URL}")
        return False

def test_create_vehicle():
    """Test 2: Create a vehicle."""
    print_section("TEST 2: Create Vehicle")
    try:
        vehicle_data = {
            "vehicle_name": "TEST-AV-001",
            "model": "Tesla Model 3 Autonomous",
            "status": "active"
        }
        response = requests.post(f"{BASE_URL}/vehicles", json=vehicle_data)
        
        if response.status_code == 201:
            vehicle = response.json()
            print("✓ Vehicle created successfully")
            print(f"  Vehicle ID: {vehicle['id']}")
            print(f"  Name: {vehicle['vehicle_name']}")
            print(f"  Model: {vehicle['model']}")
            return vehicle['id']
        elif response.status_code == 400:
            print("⚠ Vehicle already exists, getting existing vehicle...")
            # Get all vehicles and find the test vehicle
            vehicles_response = requests.get(f"{BASE_URL}/vehicles")
            vehicles = vehicles_response.json()
            for v in vehicles:
                if v['vehicle_name'] == "TEST-AV-001":
                    print(f"✓ Using existing vehicle ID: {v['id']}")
                    return v['id']
        else:
            print(f"✗ Failed to create vehicle: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_send_sensor_data(vehicle_id):
    """Test 3: Send sensor data and receive prediction."""
    print_section("TEST 3: Sensor Data Ingestion + ML Prediction")
    try:
        sensor_data = {
            "vehicle_id": vehicle_id,
            "gps_lat": 37.7749,
            "gps_lon": -122.4194,
            "speed": 55.5,
            "battery": 87.3,
            "acc_x": 0.12,
            "acc_y": -0.05,
            "acc_z": 9.81,
            "temp_motor": 65.5,
            "raw_payload": {"test": True, "sensor_version": "v2.1.0"}
        }
        
        response = requests.post(f"{BASE_URL}/sensor-data", json=sensor_data)
        
        if response.status_code == 201:
            result = response.json()
            print("✓ Sensor data ingested and predictions generated")
            print(f"  Sensor Data ID: {result['sensor_data_id']}")
            print(f"  Prediction ID: {result['prediction_id']}")
            print(f"  Failure Prediction: {result['failure']}")
            print(f"  Confidence: {result['confidence']:.2%}")
            print(f"  Anomaly Detected: {result['anomaly']}")
            print(f"  ISO Score: {result['iso_score']:.3f}")
            print(f"  Message: {result['message']}")
            return True
        else:
            print(f"✗ Failed to send sensor data: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_latest_sensor(vehicle_id):
    """Test 4: Retrieve latest sensor data."""
    print_section("TEST 4: Get Latest Sensor Data")
    try:
        response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}/latest-sensor")
        
        if response.status_code == 200:
            sensor = response.json()
            print("✓ Retrieved latest sensor data")
            print(f"  Speed: {sensor['speed']} km/h")
            print(f"  Battery: {sensor['battery']}%")
            print(f"  Motor Temp: {sensor['temp_motor']}°C")
            print(f"  Timestamp: {sensor['timestamp']}")
            return True
        else:
            print(f"✗ Failed to get sensor data: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_latest_prediction(vehicle_id):
    """Test 5: Retrieve latest prediction."""
    print_section("TEST 5: Get Latest Prediction")
    try:
        response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}/predictions/latest")
        
        if response.status_code == 200:
            prediction = response.json()
            print("✓ Retrieved latest prediction")
            print(f"  Failure: {prediction['failure_prediction']}")
            print(f"  Confidence: {prediction['failure_confidence']:.2%}")
            print(f"  Anomaly: {prediction['anomaly_flag']}")
            print(f"  Message: {prediction['message']}")
            return True
        else:
            print(f"✗ Failed to get prediction: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_create_task(vehicle_id):
    """Test 6: Create a fleet task."""
    print_section("TEST 6: Create Fleet Task")
    try:
        task_data = {
            "vehicle_id": vehicle_id,
            "task_type": "delivery",
            "pickup_location": {
                "lat": 37.7749,
                "lon": -122.4194,
                "address": "123 Market St, San Francisco"
            },
            "drop_location": {
                "lat": 37.8044,
                "lon": -122.2712,
                "address": "456 Broadway, Oakland"
            },
            "status": "assigned"
        }
        
        response = requests.post(f"{BASE_URL}/tasks", json=task_data)
        
        if response.status_code == 201:
            task = response.json()
            print("✓ Task created successfully")
            print(f"  Task ID: {task['id']}")
            print(f"  Type: {task['task_type']}")
            print(f"  Status: {task['status']}")
            return True
        else:
            print(f"✗ Failed to create task: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_tasks(vehicle_id):
    """Test 7: Get vehicle tasks."""
    print_section("TEST 7: Get Vehicle Tasks")
    try:
        response = requests.get(f"{BASE_URL}/tasks/{vehicle_id}")
        
        if response.status_code == 200:
            tasks = response.json()
            print(f"✓ Retrieved {len(tasks)} task(s)")
            for task in tasks:
                print(f"  - Task {task['id']}: {task['task_type']} ({task['status']})")
            return True
        else:
            print(f"✗ Failed to get tasks: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_maintenance(vehicle_id):
    """Test 8: Get maintenance logs."""
    print_section("TEST 8: Get Maintenance Logs")
    try:
        response = requests.get(f"{BASE_URL}/maintenance/{vehicle_id}")
        
        if response.status_code == 200:
            logs = response.json()
            print(f"✓ Retrieved {len(logs)} maintenance log(s)")
            for log in logs:
                ai_flag = "AI-Predicted" if log['predicted_by_ai'] else "Manual"
                print(f"  - {log['issue_type']}: {log['severity']} ({log['status']}) [{ai_flag}]")
            return True
        else:
            print(f"Failed to get maintenance logs: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_authentication():
    """Test 9: User registration and login."""
    print_section("TEST 9: Authentication")
    try:
        # Register
        register_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpass123",
            "role": "owner"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if response.status_code in [201, 400]:  # 400 if already exists
            if response.status_code == 201:
                print("✓ User registered successfully")
            else:
                print("⚠ User already exists (OK)")
            
            # Login
            login_data = {
                "email": "test@example.com",
                "password": "testpass123"
            }
            
            login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                result = login_response.json()
                print("✓ Login successful")
                print(f"  User: {result['user']['name']}")
                print(f"  Role: {result['user']['role']}")
                print(f"  Token: {result['access_token'][:20]}...")
                return True
            else:
                print(f"✗ Login failed: {login_response.status_code}")
                return False
        else:
            print(f"✗ Registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("  FLEET MANAGEMENT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    if not results[0][1]:
        print("\n❌ Server is not running. Please start the backend first:")
        print("   uvicorn app.main:app --reload")
        return
    
    # Test 2: Create vehicle
    vehicle_id = test_create_vehicle()
    results.append(("Create Vehicle", vehicle_id is not None))
    
    if vehicle_id is None:
        print("\n❌ Cannot continue tests without a vehicle")
        return
    
    # Test 3-8: Test with the vehicle
    results.append(("Sensor Data + Prediction", test_send_sensor_data(vehicle_id)))
    time.sleep(0.5)  # Small delay between requests
    
    results.append(("Get Latest Sensor", test_get_latest_sensor(vehicle_id)))
    time.sleep(0.5)
    
    results.append(("Get Latest Prediction", test_get_latest_prediction(vehicle_id)))
    time.sleep(0.5)
    
    results.append(("Create Task", test_create_task(vehicle_id)))
    time.sleep(0.5)
    
    results.append(("Get Tasks", test_get_tasks(vehicle_id)))
    time.sleep(0.5)
    
    results.append(("Get Maintenance Logs", test_get_maintenance(vehicle_id)))
    time.sleep(0.5)
    
    results.append(("Authentication", test_authentication()))
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    run_all_tests()
