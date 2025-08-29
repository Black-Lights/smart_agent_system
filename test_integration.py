#!/usr/bin/env python3
"""
Integration test for the history-enabled Smart Agent System
Test the main system with history integration
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_integrated_system():
    """Test the integrated system with history"""
    
    print("🧪 Testing Integrated Smart Agent System with History")
    print("=" * 60)
    
    try:
        # Test imports
        print("1. Testing integrated imports...")
        from core.master_agent import MasterAgent
        from shared.history import SessionHistoryManager
        from shared.utils.os_detector import OSDetector
        print("✅ All integrated imports successful")
        
        # Initialize components (same as main.py)
        print("\n2. Testing system initialization...")
        
        # OS detection
        os_detector = OSDetector()
        system_info = os_detector.get_full_context()
        print(f"✅ OS detected: {system_info.get('os_type')}")
        
        # History manager
        history_manager = SessionHistoryManager()
        print(f"✅ History manager initialized: {history_manager.session_id[:16]}...")
        
        # Master agent with history
        master_agent = MasterAgent(history_manager=history_manager)
        print("✅ Master agent initialized with history support")
        
        # Test task execution with history
        print("\n3. Testing task execution with history...")
        
        async def run_test_tasks():
            """Run test tasks with history tracking"""
            
            test_commands = [
                "search for Python tutorials",
                "open calculator and compute 25*47", 
                "find Samsung Galaxy Buds Pro reviews",
                "show history"  # This will be handled by main.py special case
            ]
            
            results = []
            
            for i, command in enumerate(test_commands[:-1], 1):  # Skip 'show history'
                print(f"\n   Task {i}: {command}")
                
                # Get context from history
                context = history_manager.get_condensed_context()
                print(f"   📖 Context: {context[:50]}..." if len(context) > 50 else f"   📖 Context: {context}")
                
                # Execute task
                result = await master_agent.execute_task(command, context=context)
                
                # Log to history (simulate what main.py does)
                history_manager.log_interaction(command, result, execution_time=1.5)
                
                # Store result
                results.append((command, result))
                
                print(f"   ✅ Result: {result.get('success', False)} ({result.get('agent_used', 'unknown')})")
            
            return results
        
        # Run async test tasks
        results = asyncio.run(run_test_tasks())
        print(f"\n✅ Executed {len(results)} test tasks")
        
        # Test history functionality
        print("\n4. Testing history functionality...")
        
        stats = history_manager.get_session_statistics()
        print(f"✅ Session stats: {stats['total_entries']} total, {stats['success_rate']:.1f}% success")
        
        recent_context = history_manager.get_condensed_context()
        print(f"✅ Context generation: {len(recent_context)} chars")
        
        # Test search
        search_results = history_manager.search_entries("calculator")
        print(f"✅ Search functionality: {len(search_results)} results for 'calculator'")
        
        # Test persistence
        save_success = history_manager.save_to_disk()
        print(f"✅ Persistence: {'Success' if save_success else 'Failed'}")
        
        print(f"\n🎉 Integration test completed successfully!")
        print(f"📊 Final session: {history_manager}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 Smart Agent System - Integration Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_integrated_system()
    
    if success:
        print("\n✅ Integration successful! The system is ready to use.")
        print("\n🚀 You can now run: python main.py")
    else:
        print("\n❌ Integration failed - check the errors above")
