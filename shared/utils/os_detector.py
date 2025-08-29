# ================================
# shared/utils/os_detector.py
# ================================

import os
import platform
import subprocess
from typing import Dict, Any

class OSDetector:
    """
    Advanced OS and environment detection
    Provides context for optimal automation strategies
    """
    
    def __init__(self):
        """Initialize OS detector"""
        self.os_type = platform.system()
        self.platform_info = platform.platform()
        
    def get_full_context(self) -> Dict[str, Any]:
        """Get comprehensive system context"""
        
        context = {
            'os_type': self.os_type,
            'platform': self.platform_info,
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0]
        }
        
        if self.os_type == "Linux":
            context.update(self._get_linux_context())
        elif self.os_type == "Windows":
            context.update(self._get_windows_context())
        elif self.os_type == "Darwin":
            context.update(self._get_macos_context())
        
        return context
    
    def _get_linux_context(self) -> Dict[str, Any]:
        """Get Linux-specific context"""
        
        context = {}
        
        try:
            # Get distribution info
            with open("/etc/os-release", "r") as f:
                os_release = f.read()
                if "Ubuntu" in os_release:
                    context['distribution'] = "Ubuntu"
                elif "Fedora" in os_release:
                    context['distribution'] = "Fedora"
                elif "Debian" in os_release:
                    context['distribution'] = "Debian"
                else:
                    context['distribution'] = "Linux"
        except:
            context['distribution'] = "Unknown Linux"
        
        # Get desktop environment
        context['desktop_environment'] = os.environ.get('XDG_CURRENT_DESKTOP', 'Unknown')
        
        # Get shell
        context['shell'] = os.environ.get('SHELL', '/bin/bash')
        
        return context
    
    def _get_windows_context(self) -> Dict[str, Any]:
        """Get Windows-specific context"""
        return {
            'version': platform.win32_ver()[0],
            'edition': platform.win32_edition(),
        }
    
    def _get_macos_context(self) -> Dict[str, Any]:
        """Get macOS-specific context"""
        return {
            'version': platform.mac_ver()[0]
        }