#!/usr/bin/env python3
"""
Simple test script to verify Social Media Forge backend functionality
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing Social Media Forge Backend...")
        
        # Test 1: Health check
        print("\n1. Testing health check...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test 2: Root endpoint
        print("\n2. Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print("✅ Root endpoint working")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
        
        # Test 3: API documentation
        print("\n3. Testing API documentation...")
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✅ API documentation accessible")
            else:
                print(f"❌ API documentation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ API documentation error: {e}")
        
        # Test 4: Authentication endpoint (should fail without credentials)
        print("\n4. Testing authentication endpoint...")
        try:
            response = await client.get(f"{base_url}/api/v1/auth/me")
            if response.status_code == 401:
                print("✅ Authentication endpoint working (correctly requires auth)")
            else:
                print(f"❌ Authentication endpoint unexpected response: {response.status_code}")
        except Exception as e:
            print(f"❌ Authentication endpoint error: {e}")
        
        print("\n🎉 Backend tests completed!")
        print(f"\n📱 Backend URL: {base_url}")
        print(f"📚 API Docs: {base_url}/docs")
        print(f"🔐 Test login with: admin@example.com / JustinIsNotReallySocial%789")


if __name__ == "__main__":
    asyncio.run(test_backend())
