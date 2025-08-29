# ================================
# main.py - System Entry Point
# ================================

#!/usr/bin/env python3
"""
Smart Agent System - Main Entry Point
Multi-Agent Desktop Automation with Browser Use + Desktop Control

Author: Ammar (Black-Lights)
GitHub: https://github.com/Black-Lights/smart_agent_system
License: MIT

Powered by Browser Use (https://github.com/browser-use/browser-use)
"""

import asyncio
import sys
import os
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.master_agent import MasterAgent
    from shared.utils.os_detector import OSDetector
    from shared.history import SessionHistoryManager
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("🔧 Creating placeholder modules...")
    sys.exit(1)

def main():
    """Main entry point for the Smart Agent System"""
    
    console = Console()
    
    # Display startup banner
    console.print(Panel.fit(
        Text("🤖 Smart Agent System", style="bold blue") + 
        Text("\nBrowser Use + Desktop Automation", style="italic"),
        title="🚀 Starting System",
        border_style="blue"
    ))
    
    # Initialize system
    try:
        # Detect system environment
        os_detector = OSDetector()
        system_info = os_detector.get_full_context()
        
        console.print(f"🖥️  System: {system_info.get('os_type')} - {system_info.get('desktop_environment')}")
        
        # Initialize history manager
        history_manager = SessionHistoryManager()
        console.print(f"📖 Session History initialized (ID: {history_manager.session_id[:16]}...)")
        
        # Initialize master agent with history
        master_agent = MasterAgent(history_manager=history_manager)
        
        console.print("✅ System initialized successfully!")
        console.print("\n💡 Example commands:")
        console.print("  • find the best Samsung earphones")  
        console.print("  • open calculator and compute 25*47")
        console.print("  • research Python tutorials and save links to file")
        console.print("  • show my session history")
        
        # Main interaction loop
        while True:
            try:
                console.print("\n" + "="*50)
                user_input = input("🎯 What would you like me to do? (or 'quit'): ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    # Save session before quitting
                    history_manager.save_to_disk()
                    console.print("💾 Session saved!")
                    break
                
                if not user_input.strip():
                    continue
                
                # Handle special history commands
                if user_input.lower() in ['history', 'show history', 'show my session history']:
                    stats = history_manager.get_session_statistics()
                    console.print(f"\n📊 Session Statistics:")
                    console.print(f"   Total commands: {stats['total_entries']}")
                    console.print(f"   Success rate: {stats['success_rate']:.1f}%")
                    console.print(f"   Agent usage: {stats['agent_usage']}")
                    console.print(f"   Session duration: {stats['session_duration_minutes']:.1f} minutes")
                    
                    # Show recent history
                    recent = history_manager.get_recent_entries(5)
                    console.print(f"\n📝 Recent Actions:")
                    for i, entry in enumerate(recent, 1):
                        status = "✅" if entry.task_status == "success" else "❌"
                        console.print(f"   {i}. {status} {entry.user_command} ({entry.agent_type})")
                    continue
                
                # Get context from history
                context = history_manager.get_condensed_context()
                
                # Execute task via master agent
                console.print(f"\n🔄 Processing: {user_input}")
                start_time = time.time()
                
                # Run async task with context
                result = asyncio.run(master_agent.execute_task(user_input, context=context))
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Log interaction to history
                history_manager.log_interaction(user_input, result, execution_time=execution_time)
                
                # Display result
                if result.get('success'):
                    console.print("✅ Task completed successfully!", style="green")
                    if result.get('data'):
                        console.print(f"📊 Result: {result['data']}")
                else:
                    console.print(f"❌ Task failed: {result.get('error', 'Unknown error')}", style="red")
                    
            except KeyboardInterrupt:
                console.print("\n👋 Interrupted by user")
                break
            except Exception as e:
                console.print(f"❌ Error: {e}", style="red")
                
    except Exception as e:
        console.print(f"❌ System initialization failed: {e}", style="red")
        return 1
    
    console.print("\n👋 Smart Agent System shutting down...")
    return 0

if __name__ == "__main__":
    sys.exit(main())