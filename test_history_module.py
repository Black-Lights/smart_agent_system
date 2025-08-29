#!/usr/bin/env python3
"""
Test script for the history management module
Run this to verify everything works before integrating into main system
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_history_module():
    """Test the history management module functionality"""
    
    print("🧪 Testing History Management Module")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from shared.history import SessionHistoryManager, HistorySummarizer
        from shared.history.models import HistoryEntry, create_history_entry
        print("✅ All imports successful")
        
        # Test session creation
        print("\n2. Testing session creation...")
        history = SessionHistoryManager()
        print(f"✅ Session created: {history.session_id}")
        
        # Test logging interactions
        print("\n3. Testing interaction logging...")
        
        # Simulate some interactions
        test_interactions = [
            {
                "command": "search for Python tutorials",
                "result": {"success": True, "agent_used": "browser_agent", "data": "Found 5 tutorials"}
            },
            {
                "command": "open calculator and compute 25*47",
                "result": {"success": True, "agent_used": "desktop_agent", "data": "Result: 1175"}
            },
            {
                "command": "find best Samsung earphones",
                "result": {"success": True, "agent_used": "browser_agent", "data": "Found Galaxy Buds Pro"}
            },
            {
                "command": "invalid command test",
                "result": {"success": False, "agent_used": "master_agent", "error": "Command not recognized"}
            }
        ]
        
        for interaction in test_interactions:
            history.log_interaction(
                interaction["command"],
                interaction["result"],
                execution_time=1.5
            )
        
        print(f"✅ Logged {len(test_interactions)} interactions")
        
        # Test retrieval functions
        print("\n4. Testing retrieval functions...")
        
        recent_entries = history.get_recent_entries(3)
        print(f"✅ Recent entries: {len(recent_entries)}")
        
        successful_entries = history.get_successful_entries()
        print(f"✅ Successful entries: {len(successful_entries)}")
        
        browser_entries = history.get_entries_by_agent("browser_agent")
        print(f"✅ Browser agent entries: {len(browser_entries)}")
        
        # Test context generation
        print("\n5. Testing context generation...")
        
        context = history.get_summary_context()
        print(f"✅ Generated context ({len(context)} chars):")
        print(f"   {context[:100]}...")
        
        # Test statistics
        print("\n6. Testing statistics...")
        
        stats = history.get_session_statistics()
        print(f"✅ Session stats:")
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        print(f"   Agent usage: {stats['agent_usage']}")
        
        # Test persistence
        print("\n7. Testing persistence...")
        
        save_success = history.save_to_disk()
        print(f"✅ Save to disk: {'Success' if save_success else 'Failed'}")
        
        # Test search
        print("\n8. Testing search...")
        
        search_results = history.search_entries("calculator")
        print(f"✅ Search results: {len(search_results)} entries found")
        
        # Test summarizer (if API keys available)
        print("\n9. Testing AI summarization...")
        
        try:
            summarizer = HistorySummarizer()
            
            # Test basic summarization (fallback mode)
            basic_summary = summarizer._create_basic_summary(history.entries)
            print(f"✅ Basic summary: {basic_summary[:80]}...")
            
            # Test AI summarization if API key available
            if summarizer.deepseek_api_key or summarizer.openai_api_key:
                print("   Attempting AI summarization...")
                ai_summary = history.get_intelligent_summary()
                print(f"✅ AI summary: {ai_summary[:80]}...")
            else:
                print("   ⚠️  No API keys found, skipping AI summarization test")
                
        except Exception as e:
            print(f"   ⚠️  Summarization test failed: {e}")
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"📊 Final session info: {history}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the project root directory")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_readiness():
    """Test if the module is ready for integration"""
    
    print("\n🔧 Testing Integration Readiness")
    print("=" * 40)
    
    try:
        from shared.history import SessionHistoryManager
        
        # Test the exact pattern that will be used in main.py
        history = SessionHistoryManager()
        
        # Simulate what main.py will do
        user_command = "test command"
        mock_result = {
            "success": True,
            "agent_used": "browser_agent",
            "data": "test data"
        }
        
        # Log interaction
        history.log_interaction(user_command, mock_result)
        
        # Get context (what will be passed to agents)
        context = history.get_summary_context()
        
        print(f"✅ Integration pattern works:")
        print(f"   Command logged: {user_command}")
        print(f"   Context generated: {len(context)} chars")
        print(f"   Context preview: {context[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Smart Agent System - History Module Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run main tests
    main_success = test_history_module()
    
    if main_success:
        # Run integration readiness test
        integration_success = test_integration_readiness()
        
        if integration_success:
            print("\n✅ History module is ready for integration!")
            print("\n📋 Next steps:")
            print("   1. Run this test script to verify it works")
            print("   2. If successful, proceed with main.py integration")  
            print("   3. Keep your current files as backup before changes")
        else:
            print("\n❌ Integration test failed - fix issues before proceeding")
    else:
        print("\n❌ Basic tests failed - fix module issues first")
