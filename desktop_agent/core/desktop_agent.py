# ================================
# desktop_agent/core/desktop_agent.py
# ================================

import os
import time
import json
from typing import Dict, Any, List
import pyautogui
import subprocess
import platform

class DesktopAgent:
    """
    Desktop automation agent using PyAutoGUI + OCR + UI Detection
    Handles file management, applications, system control
    """
    
    def __init__(self):
        """Initialize Desktop automation agent"""
        self.agent_type = "desktop"
        self.capabilities = [
            "file_management", "app_control", "system_settings", 
            "terminal_commands", "calculations", "screenshots"
        ]
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        print("💻 Desktop Agent initialized with PyAutoGUI")
    
    async def execute_task(self, command: str) -> Dict[str, Any]:
        """
        Execute desktop task using PyAutoGUI and system integration
        
        Args:
            command: Natural language command for desktop automation
            
        Returns:
            Execution result with action details
        """
        
        print(f"💻 Desktop Agent executing: {command}")
        
        try:
            # Analyze command type
            task_type = self._classify_desktop_task(command)
            
            # Execute based on task type
            if task_type == "calculator":
                return await self._handle_calculator_task(command)
            elif task_type == "screenshot":
                return await self._handle_screenshot_task(command)
            elif task_type == "file_management":
                return await self._handle_file_task(command)
            elif task_type == "app_control":
                return await self._handle_app_task(command)
            else:
                return await self._handle_generic_task(command)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent': 'desktop_agent',
                'command': command
            }
    
    def _classify_desktop_task(self, command: str) -> str:
        """Classify desktop task type"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['calculator', 'calculate', 'compute', 'math']):
            return "calculator"
        elif any(word in command_lower for word in ['screenshot', 'capture', 'screen']):
            return "screenshot"
        elif any(word in command_lower for word in ['file', 'folder', 'document']):
            return "file_management"
        elif any(word in command_lower for word in ['open', 'start', 'launch', 'app']):
            return "app_control"
        else:
            return "generic"
    
    async def _handle_calculator_task(self, command: str) -> Dict[str, Any]:
        """Handle calculator-related tasks"""
        
        try:
            # Open calculator app
            system = platform.system()
            
            if system == "Linux":
                subprocess.Popen(["gnome-calculator"])
            elif system == "Windows":
                subprocess.Popen(["calc.exe"])
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", "Calculator"])
            
            time.sleep(2)  # Wait for app to open
            
            # Extract any numbers from command for calculation
            import re
            numbers = re.findall(r'\b\d+\b', command)
            
            result_data = {
                'success': True,
                'agent': 'desktop_agent',
                'action': 'opened_calculator',
                'command': command,
                'numbers_found': numbers
            }
            
            # If specific calculation requested, try to perform it
            if '*' in command or 'multiply' in command.lower():
                if len(numbers) >= 2:
                    # Type the calculation
                    calculation = f"{numbers[0]}*{numbers[1]}"
                    pyautogui.typewrite(calculation)
                    pyautogui.press('enter')
                    result_data['calculation_performed'] = calculation
            
            return result_data
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'task': 'calculator'}
    
    async def _handle_screenshot_task(self, command: str) -> Dict[str, Any]:
        """Handle screenshot tasks"""
        
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Save screenshot
            timestamp = int(time.time())
            screenshot_path = f"screenshots/screenshot_{timestamp}.png"
            os.makedirs("screenshots", exist_ok=True)
            screenshot.save(screenshot_path)
            
            return {
                'success': True,
                'agent': 'desktop_agent',
                'action': 'screenshot_taken',
                'file_path': screenshot_path,
                'timestamp': timestamp,
                'command': command
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'task': 'screenshot'}
    
    async def _handle_app_task(self, command: str) -> Dict[str, Any]:
        """Handle application opening/control tasks"""
        
        try:
            command_lower = command.lower()
            app_opened = None
            
            # Extract app name and attempt to open
            if 'calculator' in command_lower:
                subprocess.Popen(["gnome-calculator"])
                app_opened = "calculator"
            elif 'browser' in command_lower or 'firefox' in command_lower:
                subprocess.Popen(["firefox"])
                app_opened = "firefox"
            elif 'file' in command_lower or 'files' in command_lower:
                subprocess.Popen(["nautilus"])
                app_opened = "file_manager"
            elif 'terminal' in command_lower:
                subprocess.Popen(["gnome-terminal"])
                app_opened = "terminal"
            
            if app_opened:
                time.sleep(2)
                return {
                    'success': True,
                    'agent': 'desktop_agent',
                    'action': f'opened_{app_opened}',
                    'command': command
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not determine app to open',
                    'command': command
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'task': 'app_control'}
    
    async def _handle_file_task(self, command: str) -> Dict[str, Any]:
        """Handle file management tasks"""
        
        try:
            # Open file manager
            subprocess.Popen(["nautilus"])
            time.sleep(2)
            
            return {
                'success': True,
                'agent': 'desktop_agent', 
                'action': 'opened_file_manager',
                'command': command,
                'note': 'File manager opened - specific file operations need implementation'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'task': 'file_management'}
    
    async def _handle_generic_task(self, command: str) -> Dict[str, Any]:
        """Handle generic desktop tasks"""
        
        return {
            'success': False,
            'agent': 'desktop_agent',
            'error': 'Generic desktop task not implemented yet',
            'command': command,
            'suggestion': 'Try specific commands like "open calculator" or "take screenshot"'
        }