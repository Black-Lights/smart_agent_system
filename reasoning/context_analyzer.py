# ================================
# reasoning/context_analyzer.py  
# ================================

import platform
import os
import subprocess
from typing import Dict, Any, List

class ContextAnalyzer:
    """
    Analyzes system context and environment for optimal task execution.
    Provides OS detection, desktop environment info, and available applications.
    """
    
    def __init__(self):
        self.os_type = platform.system()
        self.desktop_env = self._detect_desktop_environment()
        self.available_apps = self._detect_available_apps()
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get comprehensive system context"""
        return {
            "os_type": self.os_type,
            "os_version": platform.platform(),
            "desktop_environment": self.desktop_env,
            "available_applications": self.available_apps,
            "browser_preferences": self._get_browser_preferences(),
            "terminal_shell": os.environ.get("SHELL", "/bin/bash"),
            "display_info": self._get_display_info()
        }
    
    def _detect_desktop_environment(self) -> str:
        """Detect Linux desktop environment"""
        if self.os_type != "Linux":
            return self.os_type
        
        desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "")
        if desktop_env:
            return desktop_env
        
        # Fallback detection
        session_env = os.environ.get("DESKTOP_SESSION", "")
        if session_env:
            return session_env
        
        return "Unknown"
    
    def _detect_available_apps(self) -> Dict[str, bool]:
        """Detect which applications are available on the system"""
        
        common_apps = {
            # Browsers
            "firefox": "firefox",
            "chrome": "google-chrome",
            "chromium": "chromium-browser",
            
            # Desktop apps
            "calculator": "gnome-calculator",
            "file_manager": "nautilus",
            "text_editor": "gedit",
            "terminal": "gnome-terminal",
            "settings": "gnome-control-center",
            
            # Media
            "vlc": "vlc",
            "screenshot": "gnome-screenshot"
        }
        
        available = {}
        for app_name, command in common_apps.items():
            try:
                subprocess.run(["which", command], check=True, 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                available[app_name] = True
            except subprocess.CalledProcessError:
                available[app_name] = False
        
        return available
    
    def _get_browser_preferences(self) -> Dict[str, Any]:
        """Determine browser preferences and capabilities"""
        browsers = {
            "firefox": "firefox",
            "chrome": "google-chrome", 
            "chromium": "chromium-browser",
            "brave": "brave-browser"
        }
        
        available_browsers = []
        for name, command in browsers.items():
            try:
                subprocess.run(["which", command], check=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                available_browsers.append(name)
            except subprocess.CalledProcessError:
                pass
        
        return {
            "available": available_browsers,
            "preferred": available_browsers[0] if available_browsers else "firefox",
            "supports_automation": len(available_browsers) > 0
        }
    
    def _get_display_info(self) -> Dict[str, Any]:
        """Get display configuration information"""
        try:
            if self.os_type == "Linux":
                # Try to get screen resolution
                result = subprocess.run(["xrandr"], capture_output=True, text=True)
                output = result.stdout
                
                # Parse primary display resolution
                for line in output.split("\n"):
                    if "*" in line and "+" in line:  # Current resolution marker
                        parts = line.split()
                        resolution = parts[0]
                        return {"primary_resolution": resolution, "display_server": "X11"}
            
            return {"primary_resolution": "unknown", "display_server": "unknown"}
            
        except Exception as e:
            return {"primary_resolution": "unknown", "error": str(e)}
    
    def get_optimal_automation_strategy(self, task_type: str) -> Dict[str, Any]:
        """Get optimal automation approach based on system capabilities"""
        
        context = self.get_full_context()
        
        strategies = {
            "browser": {
                "method": "browser_use" if context["browser_preferences"]["supports_automation"] else "fallback_gui",
                "preferred_browser": context["browser_preferences"]["preferred"],
                "automation_ready": True
            },
            "desktop": {
                "method": "pyautogui_with_ocr",
                "ui_detection": "windows_mode", 
                "ocr_engine": "tesseract",
                "automation_ready": True
            },
            "hybrid": {
                "coordination_method": "sequential_execution",
                "data_sharing": "json_files",
                "fallback_strategy": "desktop_only"
            }
        }
        
        return strategies.get(task_type, strategies["desktop"])