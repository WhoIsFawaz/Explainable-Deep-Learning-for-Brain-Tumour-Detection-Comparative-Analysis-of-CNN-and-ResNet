"""
Backend API Test Script
Run this to verify all endpoints are working correctly
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Health check passed")

def test_login():
    """Test login endpoint"""
    print("\n" + "="*70)
    print("TEST 2: User Login")
    print("="*70)
    
    session = requests.Session()
    
    login_data = {
        "email": "doctor@test.com",
        "password": "admin123"
    }
    
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    print("✓ Login successful")
    
    return session

def test_get_current_user(session):
    """Test get current user endpoint"""
    print("\n" + "="*70)
    print("TEST 3: Get Current User")
    print("="*70)
    
    response = session.get(f"{BASE_URL}/api/auth/me")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Get user info passed")

def test_prediction(session, image_path):
    """Test prediction endpoint"""
    print("\n" + "="*70)
    print("TEST 4: Brain MRI Prediction")
    print("="*70)
    
    if not Path(image_path).exists():
        print(f"⚠ Image not found: {image_path}")
        print("Skipping prediction test")
        return
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = session.post(f"{BASE_URL}/api/predict", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Predicted Label: {result['prediction']['predicted_label']}")
        print(f"Confidence: {result['prediction']['confidence']:.4f}")
        print(f"Probabilities: {result['prediction']['probabilities']}")
        print(f"Grad-CAM URLs: {result['prediction']['gradcam_urls']}")
        print("✓ Prediction successful")
        return result['prediction']['id']
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✗ Prediction failed")

def test_get_prediction(session, prediction_id):
    """Test get prediction by ID"""
    print("\n" + "="*70)
    print("TEST 5: Retrieve Prediction by ID")
    print("="*70)
    
    if not prediction_id:
        print("Skipping (no prediction ID)")
        return
    
    response = session.get(f"{BASE_URL}/api/predictions/{prediction_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Retrieve prediction passed")

def test_prediction_history(session):
    """Test prediction history endpoint"""
    print("\n" + "="*70)
    print("TEST 6: Prediction History")
    print("="*70)
    
    response = session.get(f"{BASE_URL}/api/predictions/history")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total predictions: {len(result['predictions'])}")
        if result['predictions']:
            print(f"Latest prediction: {result['predictions'][0]}")
        print("✓ History retrieval passed")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_logout(session):
    """Test logout endpoint"""
    print("\n" + "="*70)
    print("TEST 7: User Logout")
    print("="*70)
    
    response = session.post(f"{BASE_URL}/api/auth/logout")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Logout successful")

def main():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# Brain MRI Classification System - Backend API Tests")
    print("#"*70)
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Login
        session = test_login()
        
        # Test 3: Get current user
        test_get_current_user(session)
        
        # Test 4: Prediction (need sample image)
        # Update this path to a real MRI image from your test dataset
        sample_image = "../../dataset_processed/test/yes/Y1.jpg"
        prediction_id = test_prediction(session, sample_image)
        
        # Test 5: Get prediction by ID
        test_get_prediction(session, prediction_id)
        
        # Test 6: Prediction history
        test_prediction_history(session)
        
        # Test 7: Logout
        test_logout(session)
        
        print("\n" + "#"*70)
        print("# ALL TESTS COMPLETED SUCCESSFULLY! ✓")
        print("#"*70)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print("Make sure Flask server is running: python app.py")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

if __name__ == "__main__":
    main()
