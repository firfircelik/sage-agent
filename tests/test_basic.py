#!/usr/bin/env python3
"""
Basic tests for Sage Agent HTTP Server
"""

import sys
import os
import json
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_http_server_startup():
    """Test HTTP server starts correctly."""
    print("🧪 Testing HTTP Server Startup...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "src/http_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ HTTP Server started successfully")
            process.terminate()
            return True
        else:
            print("❌ HTTP Server failed to start")
            return False
    except Exception as e:
        print(f"❌ Error starting HTTP Server: {e}")
        return False


def test_health_endpoint():
    """Test health check endpoint."""
    print("\n🧪 Testing Health Endpoint...")
    
    try:
        import urllib.request
        import urllib.error
        
        with urllib.request.urlopen("http://localhost:8000/health", timeout=5) as response:
            data = json.loads(response.read().decode())
            
        if data.get("status") == "healthy":
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except urllib.error.URLError:
        print("❌ Could not connect to HTTP server")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_imports():
    """Test all core imports work."""
    print("\n🧪 Testing Core Imports...")
    
    try:
        from src.rlm import EnterpriseRLM
        print("✅ EnterpriseRLM imported")
        
        from src.http_server import app, rlm_instance
        print("✅ HTTP Server modules imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_plugin_structure():
    """Test plugin structure exists."""
    print("\n🧪 Testing Plugin Structure...")
    
    required_files = [
        "opencode-plugin/package.json",
        "opencode-plugin/tsconfig.json",
        "opencode-plugin/src/index.ts",
        "opencode-plugin/src/api/client.ts",
        "opencode-plugin/src/tools/query.ts",
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Sage Agent Basic Tests")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Plugin Structure", test_plugin_structure()))
    results.append(("Imports", test_imports()))
    results.append(("HTTP Server Startup", test_http_server_startup()))
    results.append(("Health Endpoint", test_health_endpoint()))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
