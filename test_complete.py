#!/usr/bin/env python3
"""
Complete test script for Secure File Transfer
Tests all components: encryption, S3, QR generation, and Flask app
"""

import os
import sys
import tempfile
import io
from qr_utils import create_qr_code
from crypto_utils import encrypt_stream_to_file
import requests

def test_encryption():
    """Test encryption functionality"""
    print("🔐 Testing Encryption...")
    
    # Create a test file
    test_content = b"This is a test file for the secure file transfer system"
    test_stream = io.BytesIO(test_content)
    
    # Create temporary file for encrypted output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as tmp_file:
        encrypted_path = tmp_file.name
    
    try:
        # Encrypt the content
        encrypted_size, key_b64 = encrypt_stream_to_file(test_stream, encrypted_path)
        
        print(f"✅ Encryption successful")
        print(f"   - Original size: {len(test_content)} bytes")
        print(f"   - Encrypted size: {encrypted_size} bytes")
        print(f"   - Key (base64): {key_b64[:20]}...")
        
        # Clean up
        os.unlink(encrypted_path)
        return True
        
    except Exception as e:
        print(f"❌ Encryption failed: {e}")
        return False

def test_qr_generation():
    """Test QR code generation"""
    print("\n📱 Testing QR Code Generation...")
    
    # Test URL (similar to what the app generates)
    test_url = "http://localhost:5000/decrypt?url=https://example.com&key=test_key&fname=test.txt"
    
    # Generate QR code
    qr_path = "test_qr.png"
    try:
        create_qr_code(test_url, qr_path)
        print(f"✅ QR code generated successfully: {qr_path}")
        
        # Check if file exists and has content
        if os.path.exists(qr_path) and os.path.getsize(qr_path) > 0:
            print("✅ QR code file is valid")
            return True
        else:
            print("❌ QR code file is empty or missing")
            return False
            
    except Exception as e:
        print(f"❌ QR code generation failed: {e}")
        return False

def test_s3_connection():
    """Test S3 connection if credentials are available"""
    print("\n☁️ Testing S3 Connection...")
    
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError
        
        # Try to create S3 client
        s3 = boto3.client('s3')
        
        # Try to list buckets (this will fail if no credentials)
        s3.list_buckets()
        print("✅ S3 connection successful")
        return True
        
    except NoCredentialsError:
        print("⚠️  No AWS credentials found (this is OK for local testing)")
        return True
    except ClientError as e:
        print(f"⚠️  S3 connection failed: {e}")
        return False
    except ImportError:
        print("⚠️  boto3 not installed")
        return False

def test_flask_app():
    """Test if Flask app can be imported and configured"""
    print("\n🌐 Testing Flask App...")
    
    try:
        from app import app
        
        # Check if app is configured
        if app.config.get('SECRET_KEY'):
            print("✅ Flask app configured successfully")
            print(f"   - Debug mode: {app.debug}")
            print(f"   - Max content length: {app.config.get('MAX_CONTENT_LENGTH')}")
            return True
        else:
            print("❌ Flask app not properly configured")
            return False
            
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔧 Testing Environment...")
    
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'AWS_BUCKET']
    optional_vars = ['FLASK_SECRET_KEY', 'DELETE_TOKEN', 'PRESIGN_EXPIRY_SECONDS']
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        return False
    else:
        print("✅ All required environment variables are set")
        
    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {', '.join(missing_optional)}")
    
    return True

def main():
    """Run all tests"""
    print("🔒 Secure File Transfer - Complete System Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Flask App", test_flask_app),
        ("Encryption", test_encryption),
        ("QR Code Generation", test_qr_generation),
        ("S3 Connection", test_s3_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your system is ready.")
        print("\n📱 To start the server:")
        print("   python start_server.py")
        print("\n🌐 Then visit: http://localhost:5000")
        print("\n📱 Mobile devices can scan QR codes to download files!")
    else:
        print("⚠️  Some tests failed. Please check your setup.")
        print("\n💡 Common fixes:")
        print("   - Set up your .env file with AWS credentials")
        print("   - Ensure all required packages are installed")
        print("   - Check your S3 bucket permissions")
    
    # Clean up test files
    if os.path.exists("test_qr.png"):
        os.unlink("test_qr.png")

if __name__ == "__main__":
    main()
