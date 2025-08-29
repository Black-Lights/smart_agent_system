#!/usr/bin/env python3
"""
Test script to verify all dependencies are properly installed
"""

def test_browser_use():
    try:
        from browser_use import Agent
        print("✅ Browser Use: Ready")
        return True
    except ImportError as e:
        print(f"❌ Browser Use: {e}")
        return False

def test_desktop_automation():
    try:
        import pyautogui
        import cv2
        import pytesseract
        print("✅ Desktop Automation: Ready")
        return True
    except ImportError as e:
        print(f"❌ Desktop Automation: {e}")
        return False

def test_ai_apis():
    try:
        import openai
        import anthropic
        import requests
        print("✅ AI APIs: Ready")
        return True
    except ImportError as e:
        print(f"❌ AI APIs: {e}")
        return False

def test_system_integration():
    try:
        import platform
        import subprocess
        import os
        print(f"✅ System Integration: Ready (OS: {platform.system()})")
        return True
    except ImportError as e:
        print(f"❌ System Integration: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Smart Agent System Installation...\n")
    
    tests = [
        test_browser_use,
        test_desktop_automation, 
        test_ai_apis,
        test_system_integration
    ]
    
    results = [test() for test in tests]
    
    if all(results):
        print("\n🎉 All dependencies installed successfully!")
        print("\n🚀 Ready to build your multi-agent system!")
    else:
        print("\n⚠️  Some dependencies missing. Please install missing packages.")
